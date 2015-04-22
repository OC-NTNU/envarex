#!/usr/bin/env python


from os.path import join




# FIX:
# - different subtree/substr because of postprocessing!
# - overlapping spans!

# Example:

#                pat_name     label
# 1059    ATTR1_fluctuate    change   
# 3324         PCOMP_vary    change   
# 9576   ATTR1_accumulate  increase   
# 13168  PCOMP_accumulate  increase   
# 15547     SUBJ_decrease  decrease   
#
#                                                     file  rel_tree_n  node_n
# 1059   10.1038#ismej.2009.55#abs#sent#scnlp_v3.5.1.parse           2      67   
# 3324   10.1038#ismej.2009.55#abs#sent#scnlp_v3.5.1.parse           4      80   
# 9576   10.1038#ismej.2009.55#abs#sent#scnlp_v3.5.1.parse          11       6   
# 13168  10.1038#ismej.2009.55#abs#sent#scnlp_v3.5.1.parse           9      12   
# 15547  10.1038#ismej.2009.55#abs#sent#scnlp_v3.5.1.parse          11       6   
#
#                                                  subtree
# 1059   (NP (ADJP (ADJP (JJ molecular)) (PRN (NP (NP (...   
# 3324            (NP (NP (CD O2)) (CC and) (NP (NN NO2)))   
# 9576                      (NP (NN NO) (CC and) (NN N2O))   
# 13168                     (NP (NN NO) (CC and) (NN N2O))   
# 15547   (NP (VBN accumulated) (NN NO) (CC and) (NN N2O))   
#
#                                                   substr  
# 1059   molecular oxygen ( O2 ) and nitrite ( NO2 - ) ...  
# 3324                                          O2 and NO2  
# 9576                                          NO and N2O  
# 13168                                         NO and N2O  
# 15547                             accumulated NO and N2O  

# Here both 9576 and 15547 have the same tree (11) and node (6) although
# their substr is diffenent (due to postprocessing). However, currently only
# the latter one (15547) is stored in the annots dicts. The former (9576) is
# overwritten and therefore gets lost.

# It seems this occurs regularly:

# >>> len(matches)
# 16138
#
# >>> len(matches) - len(matches[["file", "rel_tree_n", "node_n"]].drop_duplicates())
# 53
 
# A possible solution is like this:
 
# <a id="15547">
#
# <a style="color: orange; font-weight: bold" id="9576"
# title="variable = accumulated NO and N2O                                                                                 
# id = 15547                                                                                                               
# pattern = SUBJ_decrease
#
# variable = NO and N2O                                                                                             
# id = 9576                                                                                                                
# pattern = ATTR1_accumulate">
# 
# accumulated
# NO
# and
# N2O
#
# </a>
# </a>

# In this case it is still possible to link to both ids, but only the inner
# style and tooltip are shown.





COLORS = { 'increase': 'red', 
           'decrease': 'blue', 
           'change': 'green' }


# brackets escapes are lower-cased in lemmatized parse trees
BRACKETS_ESCAPES = { "-LRB-": "(", "-RRB-": ")",
                    "-LSB-": "[", "-RSB-": "]",
                    "-LCB-": "{", "-RCB-": "}",
                    "-lrb-": "(", "-rrb-": ")",
                    "-lsb-": "[", "-rsb-": "]",
                    "-lcb-": "{", "-rcb-": "}" }

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>{title}</title>
        <link href="myminimal.css" rel="stylesheet">
</head>
<body>
<div class="container">
<hr>
"""


TRAILER = """
</div>
</body>
</html>
"""

VAR_LINK = """
<a href="var_index.html#{type_id}" target="index" 
id="{token_id}" title="{tip}"
style="color: {color}; font-weight: bold" >
"""

ARTICLE_TITLE = """
<h3>[<a href="http://dx.doi.org/{doi}" target="_blank">{number}</a>] 
{title}
</h3>
"""

TIP_PART =  """variable = {variable}
label    = {label}
token id = {token_id}
type id  = {type_id}
pattern  = {pattern}
"""


    


def write_all_abstracts(parse_dir, parse_fnames, matches, var_token_index,
                    text_fname):
    with open(text_fname, "w") as outf:    
        print(HEADER.format(title="Text"), file=outf)
        
        for file_n, parse_fname in enumerate(parse_fnames):
            write_single_abstract(parse_dir, parse_fname, file_n, matches,
                              var_token_index, outf)
                    
        print(TRAILER, file=outf)


def write_single_abstract(parse_dir, parse_fname, file_n, matches,
                      var_token_index, outf):
    
    sentences = sentence_list(parse_dir, parse_fname, matches)    
    doi = "/".join(parse_fname.split("#")[:2])
    
    print(ARTICLE_TITLE.format(number=file_n + 1, 
                              title=sentences[0],
                              doi=doi), 
          file=outf)
    
    print("<ol>", file=outf)
    
    for sent in sentences[1:]:    
        print("<li>\n" + sent + "\n</li>\n", file=outf)   
        
    print("</ol><hr>", file=outf)    


def sentence_list(parse_dir, parse_fname, matches):
    annots = create_annots_table(matches, parse_fname)   
    tree_n = 0         
    sentences = []
    
    for tree in open(join(parse_dir, parse_fname))  :
        tree_n += 1
        stack = []
        node_n = 0
        closed_n = 0 
        sent = []
    
        for node in tree.split():
            node_n += 1
            #print("\tOPENING", tree_n, node_n, node)
            stack.append(node_n)
            #print(stack)
    
            try:
                annot_list = annots[tree_n, node_n]
            except KeyError:
                pass
            else:
                link_openings(annot_list, var_token_index, sent)
    
            if node.endswith(")"):
                terminal = node.split(")")[0]
                terminal = BRACKETS_ESCAPES.get(terminal, terminal)
                sent.append(terminal)
                closed_n = stack.pop()
                #print(stack)
                #print("\tCLOSED", tree_n, closed_n, node)
    
            while node.endswith(")"):
                closed_n = stack.pop()
                #print(stack)
                #print("\tCLOSED", tree_n, closed_n, node)
                node = node[:-1]
    
                if (tree_n, closed_n) in annots:
                    n_closures = len(annots[(tree_n, closed_n)])
                    sent.append(n_closures * "</a>\n")

        sentences.append(" ".join(sent))        
    return sentences
        

def create_annots_table(matches, parse_fname):
    # create annotation table mapping (tree_n, node_n) to (token_id, row)
    selection = matches[matches["file"] == parse_fname]
    annots = {}
    
    for token_id, row in selection.iterrows(): 
        key = row["rel_tree_n"], row["node_n"]
        value = token_id, row
        annots.setdefault(key, []).append(value)
        
    return annots


def link_openings(annot_list, var_token_index, sent):
    for token_id, row in annot_list[:-1]:
        sent.append('<a id="{}">'.format(token_id))

    last_token_id, last_row = annot_list[-1]
    last_type_id = var_token_index.get(last_token_id, "?")
    
    if len(annot_list) == 1:
        color = COLORS[last_row["label"]]
    else:
        color = "orange"
            
    tip_parts = ( TIP_PART.format(token_id=token_id,
                                  type_id=var_token_index.get(token_id, "?"),
                                  label=row["label"],
                                  variable=row["substr"],                                                
                                  pattern= row["pat_name"])
                  for token_id, row in annot_list )
            
    sent.append(VAR_LINK.format(token_id=last_token_id,
                                type_id=last_type_id,
                                color=color, 
                                tip="\n".join(tip_parts)))


if __name__ == "__main__":
    import pickle
    import pandas as pd
    
    matches = pd.read_pickle("nature_abs_matches_postproc.pkl")
    
    parse_fnames = pickle.load(open("parse_fnames.pkl", "rb"))
    
    var_token_index = pickle.load(open("var_token_index.pkl", "rb"))
    
    write_all_abstracts(
        parse_dir = "/Users/work/BigData/nature/abstracts/wordparse",
        parse_fnames = parse_fnames,
        matches = matches,
        var_token_index = var_token_index,
        text_fname = "abstracts.html")

