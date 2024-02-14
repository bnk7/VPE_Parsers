"""
Code source: Kulkarni et al. (2022)
My changes:
- moved variable declarations to main()
- changed the values of some variables to match the directory structure
- simplified the reading of files
- added argparse
"""

import pickle
import os
import numpy as np
from compatibility import compatibility
from evaluation import evaluation
from collections import Counter
import math
import argparse

parser = argparse.ArgumentParser(description='Aggregate parse trees')
parser.add_argument('--test_sentences', type=str, help='The set of test sentences to input',
                    choices=['basic_VPE', 'callhome_non_VPE', 'callhome_VPE', 'coraal', 'non_VPE', 'VPE_examples'],
                    default='basic_VPE')
args = parser.parse_args()


class medcpt:
    def __init__(self, cluster_span, cluster_pos):
        self.cluster_span = cluster_span
        self.cluster_pos = cluster_pos
    def get_unique_cluster_span(self, cluster_span, cluster_pos):
        unique_cluster_span = []
        for j in range(0, len(cluster_span)):
            if cluster_span[j] not in unique_cluster_span:
                unique_cluster_span.append(cluster_span[j])
        unique_pos_span = []
        for k in range(0, len(unique_cluster_span)):
            single_cluster_pos = []
            for j in range(0, len(cluster_span)):
                if cluster_span[j] == unique_cluster_span[k]:
                    single_cluster_pos.append(cluster_pos[j])
            unique_pos_span.append(single_cluster_pos)
        self.unique_cluster_span = unique_cluster_span
        self.unique_pos_span = unique_pos_span
        return unique_cluster_span, unique_pos_span
    def get_support(self, loop_dictionary, input_parser_count, current_sentence_count):
        total_cluster_span = []
        for f in range(0, input_parser_count):
            unique_cluster_span = loop_dictionary[f]['dictionary'][current_sentence_count]['unique_cluster_span']
            total_cluster_span = total_cluster_span + unique_cluster_span

        total_unique_cluster_span = []
        for i in range(0, len(total_cluster_span)):
            if total_cluster_span[i] not in total_unique_cluster_span:
                total_unique_cluster_span.append(total_cluster_span[i])

        total_unique_cluster_support = []
        total_unique_cluster_pos = []
        for i in range(0, len(total_unique_cluster_span)):
            support = []
            pos = []
            boolean = False
            for f in range(0, input_parser_count):
                unique_cluster_span = loop_dictionary[f]['dictionary'][current_sentence_count]['unique_cluster_span']
                unique_pos_span = loop_dictionary[f]['dictionary'][current_sentence_count]['unique_pos_span']
                for j in range(0, len(unique_cluster_span)):
                    boolean = False
                    if unique_cluster_span[j] == total_unique_cluster_span[i]:
                        support.append(1)
                        pos.append(unique_pos_span[j])
                        boolean = True
                        break
                if boolean == False:
                    support.append(0)
                    empty_array = []
                    pos.append(empty_array)
            if len(support) == input_parser_count:
                total_unique_cluster_support.append(support)
                total_unique_cluster_pos.append(pos)
            else:
                difference = input_parser_count - len(support)
                for i in range(0, difference):
                    support.append(0)
                    empty_array = []
                    pos.append(empty_array)
                total_unique_cluster_support.append(support)
                total_unique_cluster_pos.append(pos)

        return total_unique_cluster_span, total_unique_cluster_support, total_unique_cluster_pos

    def get_input_parser_weight_log(self, iteration, pickle_dataset_dump_directory, folders, sentence_count, medcpt_dictionary):
        if iteration == 1:
            input_parser_weight = [1] * len(folders)
        else:
            robinson_foulds_distance_array = []
            for j in range(0, len(folders)):
                folder = folders[j]
                pickle_path = os.path.join(pickle_dataset_dump_directory, folder)
                with open(os.path.join(pickle_path, 'unique_sentence_cluster_dictionary.pickle'), 'rb') as handle:
                    unique_sentence_cluster_dictionary = pickle.load(handle)
                robinson_foulds_distance = 0
                for k in range(1, sentence_count + 1):
                    true_cluster = medcpt_dictionary[k]['medcpt_clusters']
                    predict_cluster = unique_sentence_cluster_dictionary[k]['unique_cluster_span']
                    true_error = medcpt_dictionary[k]['error']
                    predict_error = unique_sentence_cluster_dictionary[k]['error']
                    if (true_error == False) and (predict_error == False):
                        evaluation_object = evaluation(true_cluster=true_cluster, predict_cluster=predict_cluster)
                        robinson_foulds_distance = robinson_foulds_distance + evaluation_object.robinson_foulds_distance(cluster1=true_cluster, cluster2=predict_cluster)
                    elif (predict_error == False):
                        robinson_foulds_distance = robinson_foulds_distance + len(true_cluster)
                robinson_foulds_distance_array.append(robinson_foulds_distance)
        if iteration != 1:
            input_parser_weight = []
            max_value = np.max(robinson_foulds_distance_array)

            for a in range(0, len(robinson_foulds_distance_array)):
                weight = -math.log(robinson_foulds_distance_array[a]/max_value + 1e-7)
                input_parser_weight.append(weight)
        return input_parser_weight

    def get_input_parser_weight_labels_log(self, iteration, pickle_dataset_dump_directory, folders, sentence_count, medcpt_dictionary):
        if iteration == 1:
            input_parser_label_weight = [1] * len(folders)
        else:
            error_rate_array = []
            for j in range(0, len(folders)):
                folder = folders[j]
                pickle_path = os.path.join(pickle_dataset_dump_directory, folder)
                with open(os.path.join(pickle_path, 'unique_sentence_cluster_dictionary.pickle'), 'rb') as handle:
                    unique_sentence_cluster_dictionary = pickle.load(handle)
                error_rate_label = []
                for k in range(1, sentence_count + 1):
                    true_cluster = medcpt_dictionary[k]['medcpt_clusters']
                    predict_cluster = unique_sentence_cluster_dictionary[k]['unique_cluster_span']
                    true_label = medcpt_dictionary[k]['pos_aggregation']
                    predict_label = unique_sentence_cluster_dictionary[k]['unique_pos_span']
                    true_error = medcpt_dictionary[k]['error']
                    predict_error = unique_sentence_cluster_dictionary[k]['error']

                    if (true_error == False) and (predict_error == False):
                        evaluation_object = evaluation(true_cluster=true_cluster, predict_cluster=predict_cluster)
                        error_rate_label.append(
                            evaluation_object.error_rate_label(true_cluster=true_cluster, true_label=true_label,
                                                                   predict_cluster=predict_cluster,
                                                                   predict_label=predict_label))

                mean_error_rate = np.mean(error_rate_label)

                error_rate_array.append(mean_error_rate)

        if iteration != 1:
            input_parser_label_weight = []
            max_value = np.max(error_rate_array)
            for a in range(0, len(error_rate_array)):
                weight = -math.log(error_rate_array[a]/max_value + 1e-7)
                input_parser_label_weight.append(weight)

        return input_parser_label_weight

    def aggregate_clusters(self, input_parser_weight, total_unique_cluster_span, total_unique_cluster_support, total_unique_cluster_pos, error):
        if error == False:
            weighted_support = []
            sum_parser_weight = np.sum(input_parser_weight)

            for i in range(0, len(total_unique_cluster_support)):
                cluster_weight = 0
                for j in range(0, len(total_unique_cluster_support[i])):
                    cluster_weight = cluster_weight + total_unique_cluster_support[i][j] * input_parser_weight[j]
                cluster_support = cluster_weight/sum_parser_weight
                weighted_support.append(cluster_support)

            medcpt_clusters = []
            medcpt_pos = []
            temp_cluster_array = []
            temp_cluster_pos = []
            for i in range(0, len(weighted_support)):
                if weighted_support[i] > 0.5:
                    medcpt_clusters.append(total_unique_cluster_span[i])
                    medcpt_pos.append(total_unique_cluster_pos[i])
                elif weighted_support[i] == 0.5:
                    temp_cluster_array.append(total_unique_cluster_span[i])
                    temp_cluster_pos.append(total_unique_cluster_pos[i])


            if len(temp_cluster_array) > 0:
                compatibility_object = compatibility(temp_cluster_array=temp_cluster_array)
                compatible_cluster_index = compatibility_object.compatible_cluster_index(temp_cluster_array=temp_cluster_array)

                for i in range(0, len(compatible_cluster_index)):
                    medcpt_clusters.append(temp_cluster_array[compatible_cluster_index[i]])
                    medcpt_pos.append(temp_cluster_pos[compatible_cluster_index[i]])

            return medcpt_clusters, medcpt_pos
        else:
            medcpt_clusters = []
            medcpt_pos = []
            return medcpt_clusters, medcpt_pos

    def aggregate_pos_labels_bkp(self, medcpt_pos, input_parser_weight):
        pos_aggregation = []
        for i in range(0, len(medcpt_pos)):
            support = []
            pos_labels = []
            weight_pos = []
            for j in range(0, len(medcpt_pos[i])):
                for k in range(0, len(medcpt_pos[i][j])):
                    pos_labels.append(medcpt_pos[i][j][k])
                    weight_pos.append(input_parser_weight[j])
            unique_pos_labels = []
            for a in range(0, len(pos_labels)):
                if pos_labels[a] not in unique_pos_labels:
                    unique_pos_labels.append(pos_labels[a])
                    support.append(weight_pos[a])
                else:
                    for b in range(0, len(unique_pos_labels)):
                        if unique_pos_labels[b] == pos_labels[a]:
                            support[b] = support[b] + weight_pos[a]

            max_support_index = np.argmax(support)
            aggregate_pos = []
            aggregate_pos.append(unique_pos_labels[max_support_index])
            pos_aggregation.append(aggregate_pos)

        return pos_aggregation

    def aggregate_pos_labels(self, medcpt_pos, input_parser_weight):
        pos_aggregation = []
        for i in range(0, len(medcpt_pos)):
            support = []
            pos_labels = []
            weight_pos = []
            internal_count_array = []
            for j in range(0, len(medcpt_pos[i])):
                internal_count_array.append(len(medcpt_pos[i][j]))
                for k in range(0, len(medcpt_pos[i][j])):
                    pos_labels.append(medcpt_pos[i][j][k])
                    weight_pos.append(input_parser_weight[j])
            unique_pos_labels = []
            for a in range(0, len(pos_labels)):
                if pos_labels[a] not in unique_pos_labels:
                    unique_pos_labels.append(pos_labels[a])
                    support.append(weight_pos[a])
                else:
                    for b in range(0, len(unique_pos_labels)):
                        if unique_pos_labels[b] == pos_labels[a]:
                            support[b] = support[b] + weight_pos[a]

            c = Counter(internal_count_array)
            pos_labels_number = c.most_common(1)[0][0]
            if pos_labels_number == 0:
                pos_labels_number = 1
            sorted_unique_pos_labels = [x for _, x in sorted(zip(support, unique_pos_labels), reverse=True)]
            aggregate_pos = sorted_unique_pos_labels[:pos_labels_number]
            pos_aggregation.append(aggregate_pos)

        return pos_aggregation


def medcpt_aggregate_labels(input_directory, folders, sentence_count):
    pickle_dump_directory = "dictionary_pickle_files/"
    pickle_dataset_dump_directory = os.path.join(pickle_dump_directory, input_directory)
    medcpt_directory = os.path.join(pickle_dump_directory, input_directory, 'medcpt')
    with open(os.path.join(medcpt_directory, 'medcpt_aggregate_clusters_dictionary_log.pickle'), 'rb') as handle:
        medcpt_aggregate_clusters_dictionary = pickle.load(handle)

    iteration = 1
    medcpt_iteration = 3
    medcpt_object = medcpt(cluster_span=[], cluster_pos=[])
    medcpt_aggregate_labels_dictionary = {}
    input_parser_label_weight = medcpt_object.get_input_parser_weight_labels_log(iteration=iteration,
                                                                    pickle_dataset_dump_directory=pickle_dataset_dump_directory,
                                                                    folders=folders, sentence_count=sentence_count,
                                                                    medcpt_dictionary=medcpt_aggregate_labels_dictionary)
    previous_input_parser_weight = [0] * len(folders)
    weight_vector_prev_iteration = np.asarray(previous_input_parser_weight)
    weight_vector_this_iteration = np.asarray(input_parser_label_weight)
    while (iteration < 6):
        weight_vector_prev_iteration = weight_vector_this_iteration
        medcpt_aggregate_labels_dictionary[iteration] = {}
        for k in range(1, sentence_count + 1):
            medcpt_clusters = medcpt_aggregate_clusters_dictionary[medcpt_iteration][k]['medcpt_clusters']
            medcpt_pos = medcpt_aggregate_clusters_dictionary[medcpt_iteration][k]['medcpt_pos']
            error = medcpt_aggregate_clusters_dictionary[medcpt_iteration][k]['error']

            pos_aggregation = medcpt_object.aggregate_pos_labels(medcpt_pos=medcpt_pos,
                                                                 input_parser_weight=input_parser_label_weight)

            medcpt_aggregate_labels_dictionary[iteration][k] = {}
            medcpt_aggregate_labels_dictionary[iteration][k]['medcpt_clusters'] = medcpt_clusters
            medcpt_aggregate_labels_dictionary[iteration][k]['medcpt_pos'] = medcpt_pos
            medcpt_aggregate_labels_dictionary[iteration][k]['pos_aggregation'] = pos_aggregation
            medcpt_aggregate_labels_dictionary[iteration][k]['error'] = error
            print(k)
        medcpt_aggregate_labels_dictionary[iteration]['input_parser_label_weight'] = input_parser_label_weight
        iteration = iteration + 1
        input_parser_label_weight = medcpt_object.get_input_parser_weight_labels_log(iteration=iteration,
                                                                        pickle_dataset_dump_directory=pickle_dataset_dump_directory,
                                                                        folders=folders,
                                                                        sentence_count=sentence_count,
                                                                        medcpt_dictionary=
                                                                        medcpt_aggregate_labels_dictionary[
                                                                            iteration - 1])
        weight_vector_this_iteration = np.asarray(input_parser_label_weight)
        print(input_parser_label_weight)
    with open(str(medcpt_directory) + '/medcpt_aggregate_labels_dictionary_log.pickle', 'wb') as handle:
        pickle.dump(medcpt_aggregate_labels_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(str(medcpt_directory) + '/medcpt_aggregate_labels_dictionary_log.pickle', 'rb') as handle:
        medcpt_aggregate_labels_dictionary_pickle = pickle.load(handle)

    print(medcpt_aggregate_labels_dictionary_pickle == medcpt_aggregate_labels_dictionary)

    return True


def medcpt_aggregate_clusters(input_directory, folders, sentence_count):
    pickle_dump_directory = "dictionary_pickle_files"

    pickle_dataset_dump_directory = os.path.join(pickle_dump_directory, input_directory)
    medcpt_directory = os.path.join(pickle_dump_directory, input_directory, 'medcpt')
    with open(os.path.join(medcpt_directory, 'input_cluster_support_dictionary.pickle'), 'rb') as handle:
        input_cluster_support_dictionary = pickle.load(handle)

    iteration = 1
    medcpt_object = medcpt(cluster_span=[], cluster_pos=[])
    medcpt_aggregate_clusters_dictionary = {}
    input_parser_weight = medcpt_object.get_input_parser_weight_log(iteration=iteration, pickle_dataset_dump_directory= pickle_dataset_dump_directory, folders=folders, sentence_count=sentence_count, medcpt_dictionary=medcpt_aggregate_clusters_dictionary)
    previous_input_parser_weight = [0]*len(folders)
    weight_vector_prev_iteration = np.asarray(previous_input_parser_weight)
    weight_vector_this_iteration = np.asarray(input_parser_weight)
    while (iteration < 6):
        weight_vector_prev_iteration = weight_vector_this_iteration
        medcpt_aggregate_clusters_dictionary[iteration] = {}
        for k in range(1, sentence_count+1):
            total_unique_cluster_span = input_cluster_support_dictionary[k]['total_unique_cluster_span']
            total_unique_cluster_support = input_cluster_support_dictionary[k]['total_unique_cluster_support']
            total_unique_cluster_pos = input_cluster_support_dictionary[k]['total_unique_cluster_pos']
            error = input_cluster_support_dictionary[k]['error']

            medcpt_clusters, medcpt_pos = medcpt_object.aggregate_clusters(input_parser_weight= input_parser_weight, total_unique_cluster_span=total_unique_cluster_span, total_unique_cluster_support=total_unique_cluster_support,
                                                                           total_unique_cluster_pos=total_unique_cluster_pos, error=error)

            mv_pos_aggregation = medcpt_object.aggregate_pos_labels(medcpt_pos=medcpt_pos, input_parser_weight= [1]*len(folders))
            weight_pos_aggregation = medcpt_object.aggregate_pos_labels(medcpt_pos=medcpt_pos, input_parser_weight= input_parser_weight)

            medcpt_aggregate_clusters_dictionary[iteration][k] = {}
            medcpt_aggregate_clusters_dictionary[iteration][k]['medcpt_clusters'] = medcpt_clusters
            medcpt_aggregate_clusters_dictionary[iteration][k]['medcpt_pos'] = medcpt_pos
            medcpt_aggregate_clusters_dictionary[iteration][k]['mv_pos_aggregation'] = mv_pos_aggregation
            medcpt_aggregate_clusters_dictionary[iteration][k]['weight_pos_aggregation'] = weight_pos_aggregation
            medcpt_aggregate_clusters_dictionary[iteration][k]['error'] = error
            print(k)
        medcpt_aggregate_clusters_dictionary[iteration]['input_parser_weight'] = input_parser_weight
        iteration = iteration + 1
        input_parser_weight = medcpt_object.get_input_parser_weight_log(iteration=iteration,
                                                                    pickle_dataset_dump_directory=pickle_dataset_dump_directory,
                                                                    folders=folders,
                                                                    sentence_count=sentence_count,
                                                                    medcpt_dictionary=medcpt_aggregate_clusters_dictionary[iteration-1])
        weight_vector_this_iteration = np.asarray(input_parser_weight)
        print(input_parser_weight)
    with open(str(medcpt_directory) + '/medcpt_aggregate_clusters_dictionary_log.pickle', 'wb') as handle:
        pickle.dump(medcpt_aggregate_clusters_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(str(medcpt_directory) + '/medcpt_aggregate_clusters_dictionary_log.pickle', 'rb') as handle:
        medcpt_aggregate_clusters_dictionary_pickle = pickle.load(handle)

    print(medcpt_aggregate_clusters_dictionary_pickle == medcpt_aggregate_clusters_dictionary)

    return True


def unique_cluster_main(input_directory, folders, sentence_count):
    pickle_dump_directory = "dictionary_pickle_files/"
    directory = os.path.join(pickle_dump_directory, input_directory)

    for f, folder in enumerate(folders):
        pickle_path = os.path.join(directory, folder)
        with open(str(pickle_path) + '/sentence_cluster_dictionary.pickle', 'rb') as handle:
            sentence_cluster_dictionary = pickle.load(handle)
        unique_sentence_cluster_dictionary = {}
        for k in range(1, sentence_count+1):
            cluster_span = sentence_cluster_dictionary[k]['cluster_span']
            cluster_pos = sentence_cluster_dictionary[k]['cluster_pos']
            error = sentence_cluster_dictionary[k]['error']
            if not error:
                medcpt_object = medcpt(cluster_span=cluster_span, cluster_pos=cluster_pos)
                unique_cluster_span, unique_pos_span = medcpt_object.get_unique_cluster_span(cluster_span=cluster_span, cluster_pos=cluster_pos)
                unique_sentence_cluster_dictionary[k] = {}
                unique_sentence_cluster_dictionary[k]['unique_cluster_span'] = unique_cluster_span
                unique_sentence_cluster_dictionary[k]['unique_pos_span'] = unique_pos_span
                unique_sentence_cluster_dictionary[k]['error'] = error
            else:
                unique_sentence_cluster_dictionary[k] = {}
                unique_sentence_cluster_dictionary[k]['unique_cluster_span'] = []
                unique_sentence_cluster_dictionary[k]['unique_pos_span'] = []
                unique_sentence_cluster_dictionary[k]['error'] = error

        with open(str(pickle_path) + '/unique_sentence_cluster_dictionary.pickle', 'wb') as handle:
            pickle.dump(unique_sentence_cluster_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(str(pickle_path) + '/unique_sentence_cluster_dictionary.pickle', 'rb') as handle:
            unique_sentence_cluster_dictionary_pickle = pickle.load(handle)

        print(unique_sentence_cluster_dictionary_pickle == unique_sentence_cluster_dictionary)

    return True


def support_main(input_directory, folders, sentence_count):
    pickle_dump_directory = "dictionary_pickle_files/"
    directory = os.path.join(pickle_dump_directory, input_directory)

    loop_dictionary = {}
    for f, folder in enumerate(folders):
        loop_dictionary[f] = {}
        pickle_path = os.path.join(directory, folder)
        with open(str(pickle_path) + '/unique_sentence_cluster_dictionary.pickle', 'rb') as handle:
            unique_sentence_cluster_dictionary = pickle.load(handle)
        loop_dictionary[f]['dictionary'] = unique_sentence_cluster_dictionary

    input_cluster_support_dictionary = {}
    input_parser_count = len(folders)
    for k in range(1, sentence_count + 1):
        current_sentence_count = k
        input_cluster_support_dictionary[current_sentence_count] = {}
        medcpt_object = medcpt(cluster_span=[], cluster_pos=[])
        total_unique_cluster_span, total_unique_cluster_support, total_unique_cluster_pos = medcpt_object.get_support(loop_dictionary=loop_dictionary, input_parser_count=input_parser_count, current_sentence_count=current_sentence_count)
        input_cluster_support_dictionary[current_sentence_count]['total_unique_cluster_span'] = total_unique_cluster_span
        input_cluster_support_dictionary[current_sentence_count]['total_unique_cluster_support'] = total_unique_cluster_support
        input_cluster_support_dictionary[current_sentence_count]['total_unique_cluster_pos'] = total_unique_cluster_pos
        error_boolean = False
        for f in range(0, input_parser_count):
            error = loop_dictionary[f]['dictionary'][current_sentence_count]['error']
            if (error_boolean or error):
                error_boolean = True
        input_cluster_support_dictionary[current_sentence_count]['error'] = error_boolean

    if not os.path.exists(directory):
        os.mkdir(directory)
    medcpt_directory = str(directory) + 'medcpt'
    if not os.path.exists(medcpt_directory):
        os.mkdir(medcpt_directory)

    with open(str(medcpt_directory) + '/input_cluster_support_dictionary.pickle', 'wb') as handle:
        pickle.dump(input_cluster_support_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(str(medcpt_directory) + '/input_cluster_support_dictionary.pickle', 'rb') as handle:
        input_cluster_support_dictionary_pickle = pickle.load(handle)

    print(input_cluster_support_dictionary_pickle == input_cluster_support_dictionary)

    return True


if __name__ == '__main__':
    folds = ["berkeley", "corenlp", "allennlp"]
    input_dir = args.test_sentences
    sents = len(os.listdir(os.path.join('dataset', input_dir, 'allennlp')))

    run = unique_cluster_main(input_dir, folds, sents)
    run1 = support_main(input_dir, folds, sents)
    run2 = medcpt_aggregate_clusters(input_dir, folds, sents)
    run3 = medcpt_aggregate_labels(input_dir, folds, sents)
