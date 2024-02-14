"""
Code source: Goldner (2021)
My changes:
- wrote get_tree() and get_cptam()
- added extra parsers to main()
- changed the file input structure
- added argparse
"""

import re
import os
import argparse

parser = argparse.ArgumentParser(description='Output trees to a PDF using LaTeX')
parser.add_argument('--test_sentences', type=str, help='The set of test sentences to input',
                    choices=['basic_VPE', 'callhome_non_VPE', 'callhome_VPE', 'coraal', 'non_VPE', 'VPE_examples'],
                    default='basic_VPE')
args = parser.parse_args()


head = """\\documentclass[landscape, 12pt]{article} 
\\usepackage{amsfonts}
\\usepackage{amstext}
\\usepackage{amsmath}
\\usepackage{fancyhdr}
\\usepackage{amsthm}
\\usepackage{epsfig}
\\usepackage{graphicx}
\\usepackage{multicol}
\\usepackage{tikz}
\\usepackage{amssymb}
\\usepackage[all]{xy}
\\usepackage{enumitem}
\\usepackage{forest}
\\usepackage{adjustbox}
\\usepackage[landscape]{geometry}
\\usetikzlibrary{automata, positioning, shapes, arrows}

\\begin{document}
\\begin{enumerate}"""

tail = """\\end{enumerate}
\\end{document}"""


def get_tree(num: int, path: str, parser: str) -> str:
    """
    Retrieves a stored tree that was outputted by a parser.

    :param num: sentence number
    :param path: path to the folder containing the trees
    :param parser: name of the parser
    :return: tree in bracketed notation
    """
    with open(os.path.join(path, parser, 'sentence_' + str(num) + '.txt')) as file:
        output = file.readline()
    return output


def get_cptam(num: int, directory: str) -> str:
    """
    Retrieves a stored tree that was outputted by CPTAM.

    :param num: sentence number
    :param directory: folder in which aggregated tree is stored (weighted or unweighted)
    :return: tree in bracketed notation or empty string if the file doesn't exist
    """
    file_name = os.path.join('cptam', directory, 'sentence_' + str(num) + '.txt')
    if not os.path.exists(file_name):
        return ''
    with open(file_name) as file:
        output = file.readline()
    return output


def texify_tree(s):
    s_parse_tree = s.replace("(", "[")
    s_parse_tree = s_parse_tree.replace(")", "]")
    s_parse_tree = s_parse_tree.replace("$", "\$")
    # Italicize leaves by convention
    s_parse_tree = re.sub(r'\s+(([A-Z]?[a-z]|[.,?]){1,})', r' [ \\textit{ \g<1> } ]', s_parse_tree)
    # This is specifically to deal with commas in the tree
    # which throw off forest (like a lot of things...)
    s_parse_tree = re.sub(r'\[(,)', r'[ \\textit{ \g<1> }', s_parse_tree)
    s_parse_tree = "\n \\begin{{forest}} \n\t{0}\n \\end{{forest}} \n".format(s_parse_tree)
    # adjustbox is what gets most of these to fit to the page (even in landscape)
    return "\n \\begin{{adjustbox}}{{max size={{\\textwidth}}{{\\textheight}}}} \n\t{0}\n \\end{{adjustbox}} \n".format(
        s_parse_tree)


def main():
    input_path = os.path.join('test_sentences', args.test_sentences)
    tree_path = os.path.join('dataset', args.test_sentences)
    out = open(args.test_sentences + '.tex', 'w')
    out.write(head)
    with open(input_path) as f:
        for idx, line in enumerate(f):
            # This script takes a plain text file
            # with lines of the format <entry name>:<sentence>
            temp = line.split(':')
            index = temp[0]
            text = temp[1]
            out.write("\n\n \\begin{samepage}")
            out.write("\n\n \\item  \\verb|{0}|  \n\n".format(index))
            out.write("\n\n {{\\it {0} }} \n\n".format(text.rstrip()))
            s_final = texify_tree(get_tree(idx + 1, tree_path, 'corenlp'))
            b_final = texify_tree(get_tree(idx + 1, tree_path, 'berkeley'))
            a_final = texify_tree(get_tree(idx + 1, tree_path, 'allennlp'))
            c_final = texify_tree(get_cptam(idx + 1, os.path.join('unweighted', args.test_sentences)))
            c2 = get_cptam(idx + 1, os.path.join('weighted', args.test_sentences))
            out.write("\\begin{itemize} \n\n \\item {\\bf Stanford Parser (CoreNLP):} \n\n ")
            out.write(s_final)
            out.write("\n\n \\item {\\bf Berkeley Parser: } \n\n")
            out.write(b_final)
            out.write("\n\n \\item {\\bf AllenNLP Parser: } \n\n")
            out.write(a_final)
            out.write("\n\n \\item {\\bf CPTAM Parse Aggregation: } \n\n")
            out.write(c_final)
            if c2 != '':
                c2_final = texify_tree(c2)
                out.write("\n\n \\item {\\bf CPTAM Parse Aggregation (weighted): } \n\n")
                out.write(c2_final)
            out.write("\\end{itemize}")
            out.write("\n\n \\end{samepage}")
    out.write(tail)
    # this assumes you have LaTeX installed and working
    # with the pdflatex command
    # subprocess.run(['pdflatex', out_name])


if __name__ == "__main__":
    main()
