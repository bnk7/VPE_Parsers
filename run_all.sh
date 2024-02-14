#!/usr/bin/env bash

python create_trees.py --test_sentences $1
python resources.py --test_sentences $1
python medcpt.py --test_sentences $1
python print_trees.py --test_sentences $1
python to_latex.py --test_sentences $1
