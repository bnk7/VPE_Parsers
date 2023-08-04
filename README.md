# Parsing Sentences Containing VPE

This repository draws from Goldner (2021) and Kulkarni et al. (2022) to explore how various existing
constituency parsers and aggregation methods handle sentences containing verb phrase ellipsis (VPE), with the goal of 
using one of these parsers in an effort to automatically detect instances of VPE from raw text.
The final output is a LaTeX file to display the trees for easy comparison.
Some code is directly copied from these two sources, and I specify within the files when code is not my own.

## Setup
CoreNLP depends on Java, so, first, ensure you have Java downloaded and its location is added to CLASSPATH.

In the terminal, go to the repository and run the following commands:
```
pip install -r requirements.txt
pip install allennlp==2.10.1 allennlp-models==2.10.1
python -m spacy download en_core_web_md
```

Run the following in Python:
```
import stanza
stanza.install_corenlp()
```

## Execution Flow
1. create_trees.py
2. resources.py
3. medcpt.py
4. print_trees.py
5. to_latex.py

## Code Description
### create_trees.py
This file parses sentences using the AllenNLP (Gardner et al. 2018), Berkeley (Kitaev and Klein 2018), 
and Stanford (Manning et al. 2014) parsers and saves the output to text files.

### resources.py
This file processes the trees from the input parsers. Kulkarni et al. (2022) describe, 
"This code does character indexing of the input, obtains cluster list and stores the formatted input into a dictionary."

### medcpt.py
As Kulkarni et al. (2022) state, "This code does constituency parse tree aggregation." 
The aggregation produces two different trees:
one which weights the input parsers and one which doesn't. The output is stored in pickle files.

### print_trees.py
This file takes the output of medcpt.py and converts it to trees in bracketed notation. The trees are
printed to the console and written to text files. The version with the weighted parsers is only considered when it is 
different from the unweighted version.

### to_latex.py
This file creates a LaTeX document displaying the trees.

### compatibility.py and evaluation.py
These are dependencies for medcpt.py.

## Test Sentences
In addition to the Python scripts, this repository includes test sentences to use as input.
The sentences are drawn from Goldner (2021) and Canavan et al. (1997) and grouped by source and type.
The user should change the commented variables in each code file to switch to a different test sentence group.

## References

Canavan, Alexandra, David Graff, and George Zipperlen (1997). CALLHOME American English Speech. Linguistic Data 
Consortium.

Gardner, Matt, Joel Grus, Mark Neumann, Oyvind Tafjord, Pradeep Dasigi, Nelson F. Liu, Matthew Peters, Michael
Schmitz, and Luke Zettlemoyer (2018). AllenNLP: A deep semantic natural language processing platform. In Proc. of Workshop
for NLP Open Source Software (NLP-OSS), pages 1–6.

Goldner, Eli (2021). VP-Ellipsis-Rule-Out. https://github.com/etgld/VP-Ellipsis-Rule-Out/tree/main.

Kitaev, N. and D. Klein (2018). Constituency parsing with a self-attentive encoder. In Proc. of ACL, pages 2676–2686.

Kulkarni, Adithya, Nasim Sabetpour, Alexey Markin, Oliver Eulenstein, and Qi Li (2022). 
CPTAM: Constituency Parse Tree Aggregation Method. In Proc. of SIAM International Conference on Data Mining, 
pages 630-638. https://github.com/kulkarniadithya/CPTAM.

Manning, Christopher D., M. Surdeanu, J. Bauer, Jenny R. Finkel, S. Bethard, and D. McClosky (2014). The stanford 
corenlp natural language processing toolkit. In Proc. of ACL: System demonstrations, pages 55–60.