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
The sentences are drawn from Goldner (2021), Canavan et al. (1997), and Kendall and Farrington (2023) and grouped by 
source and type.
The user should change the commented variables in each code file to switch to a different test sentence group.

## Preliminary Analysis
In line with the goal of preparing the way for automatic rule-based detection of VPE, I include some observations about 
the quality of the trees with regard to the parsing of VPE. These are meant both as a qualitative analysis of the 
output trees and a potential starting point for a future researcher.

*Note*: When I use the word “trigger,” I refer to an auxiliary, copula, or negation that could represent an instance of verb 
phrase ellipsis.

### CPTAM trees in general
- The unweighted and weighted CPTAM trees are not significantly different. When they differ, it’s usually just by one 
or two similar labels. I don’t think one or the other performs consistently better than the other for VPE.
- CPTAM replaces any $ in a label with a lowercase letter. In the unweighted trees, it sometimes replaces constituent 
labels with a lowercase letter.
- It is possible to have a token that is not labeled with a part of speech, but just with a constituent label.
- VB* is not always dominated by a VP.
- The AllenNLP trees seem to be weighted highest in the spoken data.

### Basic VPE and wh-movement
- When the trigger is at the end of the sentence or right before a comma or conjunction, the parses are consistent and 
detection of VPE should be straightforward. The two things to watch out for in this case are wh-movement (check for WH*)
 and homophonous main verbs.
- This is also the case when the only token after the trigger is an adverb.
- The parsers perform well with simple wh-movement, but wh relative clauses that are not enclosed by commas can cause 
issues in the tree that would make VPE hard to detect.

### Subject-auxiliary inversion
- In the types of trees produced by constituency parsers (as opposed to syntacticians), it can be hard to tell the 
difference between an object and an inverted subject. If the tree groups the subject and auxiliary in a SINV or SQ, 
then you know to expect inversion, but not if it groups them in a VP.
- An example of the former case is clauses like “as did the other agencies,” which the Berkeley and AllenNLP parsers 
consistently assign the label SINV, causing CPTAM to do so too.
- If a potential instance of subject-auxiliary inversion involves a pronoun, examining the pronoun’s case could tell 
you if it is a subject or an object. Tag questions with pronouns are common in the spoken data, so this would be a 
helpful diagnostic.

### *To*
- The CPTAM trees consistently distinguish between the preposition *to* and the infinitive *to* because the Berkeley and 
AllenNLP parsers do. This is very helpful.
- The Stanford parser is the only one to split non-Standard American English contractions like wanna into a verb and 
*to*.
 The others treat them as a single verb, but this shouldn’t pose a difficulty to an automatic detector that checks the 
word forms in addition to the labels.

### Special cases for spoken data
- The parsers could not handle sentences with multiple restarts.
- The subject-verb agreement paradigm of African American English threw the parsers off a bit, but not as much as 
negation *not* occurring without a preceding copula. *not* wasn’t parsed as part of a VP.
- Repetition of potential triggers produced irregular trees but nothing that would be mistaken for VPE.
- In the CALLHOME corpus (Canavan et al. 1997), the token *xxx* appears in the transcripts when the audio isn’t clear. 
CPTAM and the parsers did just as well with the *xxx* as a live annotator would.
- The parsers all handle run-on sentences differently. The Berkeley parser appears to perform sentence segmentation, 
so it doesn’t always include the whole span of text. For the spoken data, CPTAM tends to follow the structure of the 
AllenNLP tree, even in the unweighted algorithm.
- AllenNLP is the only parser to classify the filler word *like* as UH; the others label it as VBP or IN. This could 
cause issues for automatic detection if *like* appears after a trigger.

### Conclusion
Overall, I don’t believe one input parser performs reliably better than the others. Thus, I find CPTAM to be a useful 
tool for parsing sentences containing VPE because it neutralizes the parsers’ individual quirks and creates more 
consistent trees. There are still many phenomena that the parsers and CPTAM cannot handle, especially with regard to 
spoken data, and this will pose an interesting challenge to future researchers building an automatic detection system.

## Citation
Per the request of the author, please cite Kulkarni et al. (2022) if you use the parts of this repository written by 
them.

## References
Canavan, Alexandra, David Graff, and George Zipperlen (1997). CALLHOME American English Speech. Linguistic Data 
Consortium.

Gardner, Matt, Joel Grus, Mark Neumann, Oyvind Tafjord, Pradeep Dasigi, Nelson F. Liu, Matthew Peters, Michael
Schmitz, and Luke Zettlemoyer (2018). AllenNLP: A deep semantic natural language processing platform. In Proc. of 
Workshop for NLP Open Source Software (NLP-OSS), pages 1–6.

Goldner, Eli (2021). VP-Ellipsis-Rule-Out. https://github.com/etgld/VP-Ellipsis-Rule-Out/tree/main.

Kendall, Tyler and Charlie Farrington (2023). The Corpus of Regional African American Language. Version 2023.06. 
Eugene, OR: The Online Resources for African American Language Project. https://doi.org/10.7264/1ad5-6t35.

Kitaev, N. and D. Klein (2018). Constituency parsing with a self-attentive encoder. In Proc. of ACL, pages 2676–2686.

Kulkarni, Adithya, Nasim Sabetpour, Alexey Markin, Oliver Eulenstein, and Qi Li (2022). 
CPTAM: Constituency Parse Tree Aggregation Method. In Proc. of SIAM International Conference on Data Mining, 
pages 630-638. https://github.com/kulkarniadithya/CPTAM.

Manning, Christopher D., M. Surdeanu, J. Bauer, Jenny R. Finkel, S. Bethard, and D. McClosky (2014). The stanford 
corenlp natural language processing toolkit. In Proc. of ACL: System demonstrations, pages 55–60.
