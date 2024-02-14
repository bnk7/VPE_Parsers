"""
Code source: Kulkarni et al. (2022)
My changes:
- removed hanlp
- changed the values of some variables to match the directory structure
- simplified the reading of files in dictionary_creation()
- added argparse
"""

import re
import pickle
import os
import random
import string
import argparse
letters = string.ascii_lowercase

parser = argparse.ArgumentParser(description='Process parse trees')
parser.add_argument('--test_sentences', type=str, help='The set of test sentences to input',
                    choices=['basic_VPE', 'callhome_non_VPE', 'callhome_VPE', 'coraal', 'non_VPE', 'VPE_examples'],
                    default='basic_VPE')
args = parser.parse_args()


class clusters_from_parsed_sentence:
    def __init__(self, parsed_sentence, language):
        self.parsed_sentence = parsed_sentence
        self.language = language
        self.character_array = [char for char in self.parsed_sentence]
    def get_clusters(self):
        brackets_array = []
        brackets_index_array = []
        for i in range(0, len(self.character_array)):
            if self.character_array[i] in ['(', ')']:
                brackets_array.append(self.character_array[i])
                brackets_index_array.append(i)

        cluster_bracket_index = []
        current_length_bracket_array = len(brackets_array)
        previous_length_bracket_array = 0
        while len(brackets_array) > 0:
            previous_length_bracket_array = current_length_bracket_array
            for i in range(0, len(brackets_array) - 1):
                if brackets_array[i] == '(' and brackets_array[i + 1] == ')':
                    cluster_bracket = []
                    cluster_bracket.append(brackets_index_array[i])
                    cluster_bracket.append(brackets_index_array[i + 1])
                    cluster_bracket_index.append(cluster_bracket)
                    brackets_array.pop(i)
                    brackets_array.pop(i)
                    brackets_index_array.pop(i)
                    brackets_index_array.pop(i)
                    break
                else:
                    continue
            current_length_bracket_array = len(brackets_array)
            if previous_length_bracket_array == current_length_bracket_array:
                if len(brackets_array) > 0:
                    raise Exception("Invalid number of brackets")
                break
        start_index = []
        end_index = []
        counter_index = []

        for i in range(0, len(cluster_bracket_index)):
            counter_index.append(i)
            start_index.append(cluster_bracket_index[i][0])
            end_index.append(cluster_bracket_index[i][1])

        start_index_sorted = [index for index, counter in sorted(zip(start_index, counter_index))]
        counter_index_sorted = [counter for index, counter in sorted(zip(start_index, counter_index))]
        cluster_bracket_index_sorted = []
        for i in range(0, len(counter_index_sorted)):
            cluster_bracket_index_sorted.append(cluster_bracket_index[counter_index_sorted[i]])

        self.character_clusters = []
        self.cluster_pos = []

        for i in range(0, len(cluster_bracket_index_sorted)):
            clusters = []
            for j in range(cluster_bracket_index_sorted[i][0], cluster_bracket_index_sorted[i][1] + 1):
                clusters.append(self.character_array[j])
            pos = []
            for k in range(1, len(clusters)):
                if clusters[k] != ' ':
                    pos.append(clusters[k])
                elif clusters[k] == ' ':
                    break
            self.cluster_pos.append(''.join(pos))
            self.character_clusters.append(''.join(clusters))

        self.cluster_span = []
        for i in range(0, len(self.character_clusters)):
            character_indexing_object = character_indexing(self.character_clusters[i], self.language)
            tokens = character_indexing_object.get_tokens(self.character_clusters[i])
            self.cluster_span.append(' '.join(tokens))

        return self.character_clusters, self.cluster_span, self.cluster_pos


class character_indexing:
    def __init__(self, parsed_sentence, language):
        self.parsed_sentence = parsed_sentence
        self.language = language
    def get_tokens(self, parsed_sentence):
        self.tokens = []
        words = str(parsed_sentence).split(' ')
        for word in words:
            y = re.search("\)", word)
            if y:
                self.tokens.append(word)
        for i in range(0, len(self.tokens)):
            self.tokens[i] = self.tokens[i].replace(')', '')
        return self.tokens
    def get_pos(self, parsed_sentence):
        self.pos = []
        words = str(parsed_sentence).split(' ')
        for word in words:
            y = re.search("\(", word)
            if y:
                self.pos.append(word)
        for i in range(0, len(self.pos)):
            self.pos[i] = self.pos[i].replace('(', '')
        return self.pos
    def format_parsed_sentence(self, parsed_sentence):
        parsed_sentence_backup = parsed_sentence
        formatted_characters = [char for char in parsed_sentence]
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '`', '\'', '!', '@', '#', '$', '%', '^', '&', '*', '[', ']', '-', '_', '+', '=', ';', ':', '>', '<', '|', '/', '¿½', '¿', '½', '°']
        for i in range (0, len(formatted_characters)):
            if formatted_characters[i] in numbers:
                formatted_characters[i] = random.choice(letters)
        parsed_sentence = ''.join(formatted_characters)
        tokens = self.get_tokens(parsed_sentence=parsed_sentence)
        pos = self.get_pos(parsed_sentence=parsed_sentence)
        for i in range(0, len(pos)):
            parsed_sentence = parsed_sentence.replace('(' + pos[i], '(', 1)
        sentence_without_space = ''.join(tokens)
        characters = [char for char in sentence_without_space]
        self.characters = characters
        character_index = []
        for i in range(0, len(characters)):
            character_index.append(i + 1)
        self.character_index = character_index
        formatted_characters = [char for char in parsed_sentence]
        covered = 0
        for i in range(0, len(formatted_characters)):
            for j in range(covered, len(characters)):
                if characters[j] == formatted_characters[i]:
                    formatted_characters[i] = str(character_index[j]) + '_'
                    covered = j + 1
                    break

        parsed_sentence = ''.join(formatted_characters)
        formatted_tokens = parsed_sentence.split(' ')
        covered = 0
        for i in range(0, len(formatted_tokens)):
            if formatted_tokens[i] == '(':
                formatted_tokens[i] = formatted_tokens[i] + str(pos[covered])
                covered = covered + 1
        parsed_sentence = ' '.join(formatted_tokens)
        self.formatted_parsed_sentence = parsed_sentence

        return self.formatted_parsed_sentence, self.characters, self.character_index


def dictionary_creation():
    pickle_dump_directory = "dictionary_pickle_files"
    dataset_directory = "dataset"
    folders = ["berkeley", "corenlp", "allennlp"]
    directory = os.path.join(dataset_directory, args.test_sentences)

    for folder in folders:
        path = os.path.join(directory, folder)
        sentence_dictionary = {}
        sentence_cluster_dictionary = {}
        parser_input_dictionary = {}
        for j, filename in enumerate(os.listdir(path)):
            k = j + 1
            file = os.path.join(path, filename)

            read_file = open(file, 'r')
            read_line = read_file.readline()

            parsed_sentence = read_line.rstrip()
            parser_input_dictionary[k] = {}
            parser_input_dictionary[k]['parsed_input_sentence'] = parsed_sentence
            try:
                character_indexing_object = character_indexing(parsed_sentence=parsed_sentence, language='English')
                formatted_parsed_sentence, characters, character_index = character_indexing_object.format_parsed_sentence(
                    parsed_sentence=parsed_sentence)
                clusters_from_parsed_sentence_object = clusters_from_parsed_sentence(
                    parsed_sentence=formatted_parsed_sentence, language='English')
                character_clusters, cluster_span, cluster_pos = clusters_from_parsed_sentence_object.get_clusters()
                sentence_dictionary[k] = {}
                sentence_dictionary[k]['parsed_sentence'] = parsed_sentence
                sentence_dictionary[k]['formatted_parsed_sentence'] = formatted_parsed_sentence
                sentence_dictionary[k]['characters'] = characters
                sentence_dictionary[k]['character_index'] = character_index
                sentence_dictionary[k]['character_index_size'] = len(character_index)
                sentence_dictionary[k]['error'] = False
                sentence_cluster_dictionary[k] = {}
                sentence_cluster_dictionary[k]['formatted_parsed_sentence'] = formatted_parsed_sentence
                sentence_cluster_dictionary[k]['character_clusters'] = character_clusters
                sentence_cluster_dictionary[k]['cluster_span'] = cluster_span
                sentence_cluster_dictionary[k]['cluster_pos'] = cluster_pos
                sentence_cluster_dictionary[k]['error'] = False
            except:
                sentence_dictionary[k] = {}
                sentence_dictionary[k]['parsed_sentence'] = ''
                sentence_dictionary[k]['formatted_parsed_sentence'] = ''
                sentence_dictionary[k]['characters'] = []
                sentence_dictionary[k]['character_index'] = []
                sentence_dictionary[k]['character_index_size'] = 0
                sentence_dictionary[k]['error'] = True
                sentence_cluster_dictionary[k] = {}
                sentence_cluster_dictionary[k]['formatted_parsed_sentence'] = ''
                sentence_cluster_dictionary[k]['character_clusters'] = []
                sentence_cluster_dictionary[k]['cluster_span'] = []
                sentence_cluster_dictionary[k]['cluster_pos'] = []
                sentence_cluster_dictionary[k]['error'] = True

        pickle_directory = os.path.join(pickle_dump_directory, folder)
        if not os.path.exists(pickle_dump_directory):
            os.mkdir(pickle_dump_directory)
        if not os.path.exists(pickle_directory):
            os.mkdir(pickle_directory)
        pickle_path = str(pickle_directory) + folder + '/'
        if not os.path.exists(pickle_path):
            os.mkdir(pickle_path)
        with open(str(pickle_path) + '/sentence_dictionary.pickle', 'wb') as handle:
            pickle.dump(sentence_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(str(pickle_path) + '/sentence_cluster_dictionary.pickle', 'wb') as handle:
            pickle.dump(sentence_cluster_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(str(pickle_path) + '/parser_input_dictionary.pickle', 'wb') as handle:
            pickle.dump(parser_input_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(str(pickle_path) + '/sentence_dictionary.pickle', 'rb') as handle:
            sentence_dictionary_pickle = pickle.load(handle)

        with open(str(pickle_path) + '/sentence_cluster_dictionary.pickle', 'rb') as handle:
            sentence_cluster_dictionary_pickle = pickle.load(handle)

        with open(str(pickle_path) + '/parser_input_dictionary.pickle', 'rb') as handle:
            parser_input_dictionary_pickle = pickle.load(handle)

        print(sentence_dictionary_pickle == sentence_dictionary)
        print(sentence_cluster_dictionary_pickle == sentence_cluster_dictionary)
        print(parser_input_dictionary_pickle == parser_input_dictionary)
    return True


if __name__ == '__main__':
    run = dictionary_creation()
