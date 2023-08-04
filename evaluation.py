"""
Code source: Kulkarni et al. (2022)
My changes:
- removed functions outside the class
"""


class evaluation:
    def __init__(self, true_cluster, predict_cluster):
        self.true_cluster = true_cluster
        self.predict_cluster = predict_cluster

    def robinson_foulds_distance(self, cluster1, cluster2):
        cluster1 = set(cluster1)
        cluster2 = set(cluster2)
        difference = cluster1.symmetric_difference(cluster2)
        list_difference = list(difference)
        robinsonfould_distance = len(list_difference)
        return robinsonfould_distance

    def precision_score(self, true_cluster, predict_cluster):
        TP = 0
        for i in range(0, len(predict_cluster)):
            if predict_cluster[i] in true_cluster:
                TP = TP + 1
        if len(predict_cluster) != 0:
            precision = TP / len(predict_cluster)
        else:
            precision = 0

        precision = round(precision, 2)

        return precision

    def recall_score(self, true_cluster, predict_cluster):
        TP = 0
        for i in range(0, len(true_cluster)):
            if true_cluster[i] in predict_cluster:
                TP = TP + 1
        if len(true_cluster) != 0:
            recall = TP / len(true_cluster)
        else:
            recall = 0
        recall = round(recall, 2)
        return recall

    def f1_score(self, true_cluster, predict_cluster):
        precision = self.precision_score(true_cluster=true_cluster, predict_cluster=predict_cluster)
        recall = self.recall_score(true_cluster=true_cluster, predict_cluster=predict_cluster)

        if (precision + recall) == 0:
            f1 = 0
        else:
            f1 = (2 * precision * recall) / (precision + recall)
        f1 = round(f1, 2)
        return f1

    def accuracy_score(self, true_cluster, predict_cluster):
        correct = 0
        for i in range(0, len(predict_cluster)):
            if predict_cluster[i] in true_cluster:
                correct = correct + 1
        if len(predict_cluster) != 0:
            accuracy = correct / len(predict_cluster)
        else:
            accuracy = 0
        accuracy = round(accuracy, 2)
        return accuracy

    def precision_score_label(self, true_cluster, true_label, predict_cluster, predict_label):
        TP = 0
        FP = 0
        for i in range(0, len(predict_cluster)):
            prediction_boolean = False
            for j in range(0, len(true_cluster)):
                if true_cluster[j] == predict_cluster[i]:
                    prediction_boolean = True
                    for a in range(0, len(true_label[j])):
                        ground_truth_label = str(true_label[j][a]).split('-')[0]
                        boolean = False
                        for k in range(0, len(predict_label[i])):
                            prediction_label = str(predict_label[i][k]).split('-')[0]
                            if prediction_label == ground_truth_label:
                                TP = TP + 1
                                boolean = True
                                break
                        if boolean == False:
                            FP = FP + 1
                    break
            if prediction_boolean == False:
                FP = FP + len(predict_label[i])

        if (TP + FP) == 0:
            precision = 0
        else:
            precision = (TP / (TP + FP))

        precision = round(precision, 2)
        return precision

    def accuracy_score_label(self, true_cluster, true_label, predict_cluster, predict_label):
        TP = 0
        FP = 0
        for i in range(0, len(predict_cluster)):
            for j in range(0, len(true_cluster)):
                if true_cluster[j] == predict_cluster[i]:
                    for a in range(0, len(true_label[j])):
                        ground_truth_label = str(true_label[j][a]).split('-')[0]
                        boolean = False
                        for k in range(0, len(predict_label[i])):
                            prediction_label = str(predict_label[i][k]).split('-')[0]
                            if prediction_label == ground_truth_label:
                                TP = TP + 1
                                boolean = True
                                break
                        if boolean == False:
                            FP = FP + 1
                    break

        if (TP + FP) == 0:
            accuracy = 0
        else:
            accuracy = (TP / (TP + FP))

        accuracy = round(accuracy, 2)
        return accuracy

    def error_rate_label(self, true_cluster, true_label, predict_cluster, predict_label):
        TP = 0
        FP = 0
        for i in range(0, len(predict_cluster)):
            for j in range(0, len(true_cluster)):
                if true_cluster[j] == predict_cluster[i]:
                    for a in range(0, len(true_label[j])):
                        ground_truth_label = str(true_label[j][a]).split('-')[0]
                        boolean = False
                        for k in range(0, len(predict_label[i])):
                            prediction_label = str(predict_label[i][k]).split('-')[0]
                            if prediction_label == ground_truth_label:
                                TP = TP + 1
                                boolean = True
                                break
                        if boolean == False:
                            FP = FP + 1
                    break

        if (TP + FP) == 0:
            error_rate = 0
        else:
            error_rate = (FP / (TP + FP))

        error_rate = round(error_rate, 2)
        return error_rate

    def recall_score_label(self, true_cluster, true_label, predict_cluster, predict_label):
        TP = 0
        FN = 0
        for i in range(0, len(true_cluster)):
            true_boolean = False
            for j in range(0, len(predict_cluster)):
                if predict_cluster[j] == true_cluster[i]:
                    true_boolean = True
                    for a in range(0, len(true_label[i])):
                        ground_truth_label = str(true_label[i][a]).split('-')[0]
                        boolean = False
                        for k in range(0, len(predict_label[j])):
                            prediction_label = str(predict_label[j][k]).split('-')[0]
                            if prediction_label == ground_truth_label:
                                TP = TP + 1
                                boolean = True
                                break
                        if boolean == False:
                            FN = FN + 1
                    break
            if true_boolean == False:
                FN = FN + len(true_label[i])
        if (TP + FN) == 0:
            recall = 0
        else:
            recall = (TP / (TP + FN))
        recall = round(recall, 2)
        return recall

    def f1_score_label(self, true_cluster, true_label, predict_cluster, predict_label):
        precision = self.precision_score_label(true_cluster=true_cluster, true_label=true_label,
                                          predict_cluster=predict_cluster, predict_label=predict_label)
        recall = self.recall_score_label(true_cluster=true_cluster, true_label=true_label, predict_cluster=predict_cluster,
                                    predict_label=predict_label)

        if (precision + recall) == 0:
            f1 = 0
        else:
            f1 = (2 * precision * recall) / (precision + recall)
        f1 = round(f1, 2)
        return f1
