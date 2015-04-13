import pandas as pd

from baleen.trans.wrap import transform_matches
from baleen.trans.trace import print_derivations


org_matches_fname = "../match/nature_abs_matches_postproc.pkl"

transform_fname = [
#    "coordination.tfm",
    "parenthetical.tfm",
#    "non-restrict.tfm",
#    "modifiers.tfm"
]

jython_path = "/Users/work/local/src/stanford-tregex-2014-10-26/stanford-tregex.jar"

trans_matches_fname = "nature_abs_matches_postproc_trans.pkl"

trans_matches = transform_matches(org_matches_fname,
                                  transform_fname,  
                                  trans_matches_fname,
                                  #org_tuples_fname="org_tuples",
                                  jython_path=jython_path)

print_derivations(trans_matches, "derivations.txt")


uniq_trans_matches_fname = "nature_abs_matches_postproc_trans_uniq.pkl"

# drop duplicate subtrees resulting from different derivations
trans_matches.drop_duplicates(
    subset=['label', 'file', 'rel_tree_n', 'node_n', 'subtree'], 
    inplace=True)

trans_matches.to_pickle(uniq_trans_matches_fname)
