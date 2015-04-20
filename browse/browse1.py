from os.path import join

import pandas as pd


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





colors = {'increase': 'red', 
          'decrease': 'blue', 
          'change': 'green' }


bracket_escapes = { "-LRB-": "(", "-RRB-": ")",
                    "-LSB-": "[", "-RSB-": "]",
                    "-LCB-": "{", "-RCB-": "}" }

header = """
<!DOCTYPE html>
<html lang="en">
<head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Matches</title>
        <link href="myminimal.css" rel="stylesheet">
</head>
<body>
<div class="container">
"""


trailer = """
</div>
</body>
</html>
"""

var_link = """
<a style="color: {color}; font-weight: bold" id="{id}" title="{title}">
"""

article_link = """
<h2>[{number}] 
<a href="http://dx.doi.org/{doi}" target="_blank">{doi}</a>
</h2>
"""

title_part =  """variable = {variable}
label={label}
id = {id}
pattern = {pattern}
"""

matches = pd.read_pickle("nature_abs_matches_postproc.pkl")

# files with at least two variables
file_counts = matches["file"].value_counts()
parse_fnames = sorted(file_counts[file_counts > 1].index, reverse=True)

parse_dir = "/Users/work/BigData/nature/abstracts/parse"

outf = open("matches.html", "w")

print(header, file=outf)

max_files = 1000


for file_n, parse_fname in enumerate(parse_fnames[:max_files]):
    doi = "/".join(parse_fname.split("#")[:2])
    print(article_link.format(number=file_n + 1, doi=doi), file=outf)
    
    selection = matches[matches["file"] == parse_fname]

    # create annots dict mapping (tree_n, node_n) to (id, row)
    annots = {}
    for id, row in selection.iterrows(): 
        key = row["rel_tree_n"], row["node_n"]
        value = id, row
        annots.setdefault(key, []).append(value)
    
    parse_file = open(join(parse_dir, parse_fname))    
    tree_n = 0    
    print("<ol>", file=outf)
    
    for tree in parse_file:
        tree_n += 1
        stack = []
        node_n = 0
        closed_n = 0 
        print("<li>", file=outf)
    
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
                title = "\n".join(title_part.format(id=id,
                                                    label=row["label"],
                                                    variable=row["substr"],                                                
                                                    pattern= row["pat_name"])
                                  for id, row in annot_list)
                
                for id, row in annot_list[:-1]:
                    print('<a id="{}">'.format(id), file=outf)
                    
                id, row = annot_list[-1]                    
                
                if len(annot_list) == 1:
                    color = colors[row["label"]]
                else:
                    color = "orange"
                    
                print(var_link.format(id=id,
                                      color=color, 
                                      title=title),
                      file=outf)
                
            if node.endswith(")"):
                terminal = node.split(")")[0]
                terminal = bracket_escapes.get(terminal, terminal)
                print(terminal, file=outf)
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
                    print(n_closures * "</a>", file=outf)
                    
        print("</li>\n", file=outf)      
    print("</ol><hr>", file=outf)    
            
print(trailer, file=outf)