import pickle
import pprint
import re
import os


pos_tagset = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT',
            'POS', 'PRP', 'PP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
            'WDT', 'WP', 'WP$', 'WRB', '#', '$', '.', ',', ':', '(', ')', '"', "‘", '“', "’", '”', 'HYPH', 'PRP$']
syntactic_tagset = ['ADJP', 'ADVP', 'NP', 'PP', 'S', 'SBAR', 'SBARQ', 'SINV', 'SQ', 'VP', 'WHADVP', 'WHNP', 'WHPP',
                    'X', '*', '0', 'T', 'CONJP', 'INTJ', 'FRAG', 'LST', 'NAC', 'NP-TMP', 'NML', 'NX', 'PRN', 'PRT',
                    'QP', 'RRC', 'UCP', 'WHADJP']


def is_greater(first: str, second: str) -> bool:
    """
    A helper for manually fixing the order of labels because medcpt stores the labels in reverse alphabetical order
    rather than by level and stores the clusters usually, but not always, in a pre-order traversal.

    :param first: the first label
    :param second: the second label
    :return: whether the first argument is a higher constituent than the second
    """
    if second in pos_tagset:
        return True
    # S > VP
    # S > NP
    # S > INTJ
    if first == 'S' and (second == 'VP' or second == 'NP' or second == 'INTJ'):
        return True
    # UCP > ADVP
    if first == 'UCP' and second == 'ADVP':
        return True
    # SBARQ > WHADVP
    # SBARQ > SQ
    if first == 'SBARQ' and (second == 'WHADVP' or second == 'SQ'):
        return True
    # SBAR > VP
    # SBAR > S
    # SBAR > INTJ
    if first == 'SBAR' and (second == 'VP' or second == 'S' or second == 'INTJ'):
        return True
    # VP > ADVP
    if first == 'VP' and second == 'ADVP':
        return True
    # ADJP > ADVP
    if first == 'ADJP' and second == 'ADVP':
        return True
    # ADVP > INTJ
    if first == 'ADVP' and second == 'INTJ':
        return True
    return False


def initialize(labels: list, idx_list: list) -> list:
    """
    Insert topmost node(s) into a tree represented as a list of strings making up its bracket notation.

    :param labels: syntactic tag(s) associated with the character span
    :param idx_list: original tree
    :return: updated tree
    """
    new_idx_list = idx_list.copy()
    for label in labels:
        new_idx_list.insert(0, '(' + label + ' ')
        new_idx_list.append(')')
    return new_idx_list


def add_to_pos(labels: list, idx_list: list, sent_list: list) -> list:
    """
    Insert node(s) into a tree represented as a list of strings making up its bracket notation.

    :param labels: part of speech and/or syntactic tag(s) associated with the character span
    :param idx_list: original tree
    :param sent_list: current tree
    :return: updated tree
    """
    new_sent_list = sent_list.copy()
    beg_key = idx_list[0]
    beg_idx = new_sent_list.index(beg_key, int(beg_key) - 1)

    # get previous label(s) if they exist
    prev_labels = []
    curr_idx = beg_idx
    # while there is a previous element, that element is not the empty string, and it is a label
    while curr_idx > 0 and len(new_sent_list[curr_idx - 1]) > 0 and new_sent_list[curr_idx - 1][0] == '(':
        # remove ( at beginning and space at end, then add to previous labels
        prev_labels.append(new_sent_list[curr_idx - 1][1:-1])
        curr_idx -= 1

    for j, label in enumerate(labels):
        # insert the label in the correct position
        if j > 0:
            beg_key = idx_list[0]
            # by default, insert just before the first character of the token/constituent
            beg_idx = new_sent_list.index(beg_key, int(beg_key) - 1)
        # determine the correct placement of this label relative to the surrounding ones
        for prev_label in prev_labels:
            if is_greater(label, prev_label):
                beg_idx = beg_idx - 1
        new_sent_list.insert(beg_idx, '(' + label + ' ')

        # insert a closing parenthesis
        end_key = idx_list[-1]
        end_idx = new_sent_list.index(end_key, int(end_key) - 1) + 1
        new_sent_list.insert(end_idx, ')')

        prev_labels.append(label)
    return new_sent_list


def replace_keys(sent_list: list, c_dict: dict) -> str:
    """
    Replaces number keys with the characters they represent.

    :param sent_list: final tree
    :param c_dict: dictionary mapping integer keys to characters
    :return: tree in bracketed notation
    """
    for j, item in enumerate(sent_list):
        if not re.fullmatch(r'\d+', item) is None:
            sent_list[j] = c_dict[item]
    parse = ''.join(sent_list)
    return re.sub(r'\)\(', ') (', parse)


def get_sentence_cluster(cluster_list: list) -> int:
    """
    Finds the index of the cluster in the medcpt output corresponding to the whole sentence.

    :param cluster_list: the list of clusters
    :return: the index found
    """
    max_length = 0
    index_max_length = 0
    for i, cluster in enumerate(cluster_list):
        length = len(cluster)
        if length > max_length:
            max_length = length
            index_max_length = i
    return index_max_length


def reorder(old_list: list, target_idx: int) -> list:
    """
    Moves the element at target_idx to the front of the list.

    :param old_list: list to be reordered
    :param target_idx: index of the element to be moved
    :return: reordered list
    """
    new_list = old_list.copy()
    first = new_list.pop(target_idx)
    new_list.insert(0, first)
    return new_list


def create_trees(sent: int, iteration: dict, sents: list) -> tuple:
    """
    Converts the output of CPTAM into trees.

    :param sent: sentence number
    :param iteration: dictionary output of the last iteration of medcpt
    :param sents: list of sentences as strings
    :return: tuple of trees in bracketed notation; the first one is with unweighted input parsers, and the second one with weighted input parsers
    """
    clusters = iteration[sent]['medcpt_clusters']
    pos_agg = iteration[sent]['mv_pos_aggregation']
    weighted_pos_agg = iteration[sent]['weight_pos_aggregation']

    full_sent_str = sents[sent - 1].replace(' ', '')
    char_dict = {}
    for k, c in enumerate(full_sent_str):
        key = str(k + 1)
        char_dict[key] = c

    # move the element corresponding to the whole sentence to the front
    full_sent_idx = get_sentence_cluster(clusters)
    clusters = reorder(clusters, full_sent_idx)
    pos_agg = reorder(pos_agg, full_sent_idx)
    weighted_pos_agg = reorder(weighted_pos_agg, full_sent_idx)

    full_sent_list = []
    weighted_full_sent_list = []
    for i, cluster in enumerate(clusters):
        indices = re.split(r'[ _]', cluster)[:-1]
        if i == 0:
            full_sent_list = initialize(pos_agg[0], indices)
            weighted_full_sent_list = initialize(weighted_pos_agg[0], indices)
        else:
            full_sent_list = add_to_pos(pos_agg[i], indices, full_sent_list)
            weighted_full_sent_list = add_to_pos(weighted_pos_agg[i], indices, weighted_full_sent_list)

    parse = replace_keys(full_sent_list, char_dict)
    weighted_parse = replace_keys(weighted_full_sent_list, char_dict)
    return parse, weighted_parse


def save_to_file(t: str, num: int, fold: str) -> None:
    """
    Saves a tree to a text file.

    :param t: parse tree in bracketed notation
    :param num: sentence number
    :param fold: name of the folder in which to save the file
    :return: None
    """
    output_path = 'cptam/' + fold
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(output_path + '/sentence_' + str(num) + '.txt', 'w') as f:
        f.write(t.strip())


if __name__ == '__main__':
    # CHANGE THIS VALUE TO PROCESS A DIFFERENT SET OF TEST SENTENCES
    directories = ["basic_VPE/"]

    # retrieve output of medcpt.py
    # this code adapted from Kulkarni et al. (2022)
    pickle_dump_directory = "dictionary_pickle_files/"
    dataset_directory = "dataset/"
    for d in range(0, len(directories)):
        print("Dataset: " + str(str(directories[d]).split('/')[0]))
        pickle_directory = str(pickle_dump_directory) + str(directories[d])
        medcpt_directory = str(pickle_directory) + 'medcpt'
        with open(str(medcpt_directory) + '/medcpt_aggregate_clusters_dictionary_log.pickle', 'rb') as handle:
            medcpt_aggregate_clusters_dictionary = pickle.load(handle)

    num_iterations = len(medcpt_aggregate_clusters_dictionary)
    final_iteration = medcpt_aggregate_clusters_dictionary[num_iterations]
    # pprint.pprint(final_iteration)

    # retrieve sentences
    folder = directories[0][:-1]
    sentences = []
    with open('test_sentences/' + folder) as source_file:
        for line in source_file:
            split = line.split(':')
            text = split[1].strip()
            sentences.append(text)

    # print and save trees
    for idx, sentence in enumerate(final_iteration):
        if isinstance(sentence, int):
            tree, weighted_tree = create_trees(sentence, final_iteration, sentences)
            print(sentence)
            print(tree)
            if tree != weighted_tree:
                print('With weighted parsers:')
                print(weighted_tree)
                save_to_file(weighted_tree, idx + 1, 'weighted/' + folder)
            save_to_file(tree, idx + 1, 'unweighted/' + folder)
