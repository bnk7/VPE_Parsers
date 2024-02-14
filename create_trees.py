import benepar
import spacy
from stanza.server import CoreNLPClient
from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Parse the input sentences')
parser.add_argument('--test_sentences', type=str, help='The set of test sentences to input',
                    choices=['basic_VPE', 'callhome_non_VPE', 'callhome_VPE', 'coraal', 'non_VPE', 'VPE_examples'],
                    default='basic_VPE')
args = parser.parse_args()

ben = spacy.load('en_core_web_md')
ben.add_pipe("benepar", config={"model": "benepar_en3"})
corenlp = CoreNLPClient(annotators=['parse'], timeout=30000, memory='8G')
allen = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/elmo-constituency-parser-2020.02.10.tar.gz")


def berkeley_parse(s: str) -> str:
    """
    Parses a sentence using the Berkeley parser.

    :param s: sentence to parse
    :return: tree in bracketed notation
    """
    doc = ben(s)
    sent = list(doc.sents)[0]
    return sent._.parse_string


# adapted from Goldner (2021)
def stanford_parse(s: str) -> str:
    """
    Parses a sentence using the Stanford parser from CoreNLP.

    :param s: sentence to parse
    :return: tree in bracketed notation
    """
    ann = corenlp.annotate(s, output_format='json')
    sent = ann['sentences'][0]['parse']
    # normalize output
    sent = re.sub(r'\r\n', '', sent)
    sent = re.sub(r' +', ' ', sent)
    sent = sent[6:-1]  # remove ROOT
    return sent


def allen_parse(s: str) -> str:
    """
    Parses a sentence using the AllenNLP parser.

    :param s: sentence to parse
    :return: tree in bracketed notation
    """
    output = allen.predict(s)
    return output['trees']


if __name__ == '__main__':
    # retrieve sentences to parse
    sentences = []
    with open(os.path.join('test_sentences', args.test_sentences)) as source_file:
        for line in source_file:
            split = line.split(':')
            text = split[1].strip()
            sentences.append(text)

    # set up directory structure
    parent_dir = os.path.join('dataset', args.test_sentences)
    child_dirs = ['berkeley', 'corenlp', 'allennlp']

    for child in child_dirs:
        child_path = os.path.join(parent_dir, child)
        if not os.path.exists(child_path):
            os.makedirs(child_path)

    # parse sentences and store trees
    output_files = [os.path.join(parent_dir, directory, 'sentence_') for directory in child_dirs]
    for idx, sentence in enumerate(sentences):
        berkeley_tree = berkeley_parse(sentence)
        stanford_tree = stanford_parse(sentence)
        allen_tree = allen_parse(sentence)
        trees = [berkeley_tree, stanford_tree, allen_tree]

        for tree_idx, tree in enumerate(trees):
            file_name = output_files[tree_idx] + str(idx + 1) + '.txt'
            with open(file_name, 'w') as f:
                f.write(tree)
