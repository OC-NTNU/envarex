from collections import namedtuple

import pandas as pd


header = """
<!DOCTYPE html>
<html lang="en">
<head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Variable Index</title>
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

table = """
<table class="table">
     <col width="20%" />
     <tr>
          <th scope="row">Variable ({var_n}):</th>
          <td><a name="{var_id}">{var}</a></td>
     </tr>
     <tr>
          <th scope="row">Changing ({change_n}):</th>  
          <td style="color: green">{change_links}</td>
     </tr>
     <tr>
          <th scope="row">Increasing ({increase_n}):</th>
          <td style="color: red">{increase_links}</td>
     </tr>
     <tr>
          <th scope="row">Decreasing ({decrease_n}):</th>
          <td style="color: blue">{decrease_links}</td>
     </tr>
     <tr>
          <th scope="row">More general:</th>
          <td><ul>{generals}</ul></td>
     </tr>
     <tr>
          <th scope="row">More specific:</th>
          <td><ul>{specifics}</ul></td>
     </tr>
</table>
"""

link = ( '<a ' 
         'href="matches.html#{{id}}" '
         'target="matches" '
         'style="color: {color}">'
         '#{{id}}'
         '</a>' )

change_link = link.format(color="green")
incr_link = link.format(color="red")
decr_link = link.format(color="blue")  


var_link = '<li><a href="#{id}">{text}</a></li>'


# A Variable instance represents variable *type*.
# The 'change', 'increase' and 'decrease' sets hold variable *tokens*,
# i.e., unique identifiers of text spans in the text (mentions).
# The 'generals' and 'specifics' sets hold variable *types*,
# i.e., keys of other Variable instances in the index. 
Variable = namedtuple("Variable", 
                      ["change", "increase", "decrease", 
                       "generals", "specifics"])


def create_index(matches):
     index = {}
     
     for id, row in matches.iterrows():
          substr = row["substr"]
          var = index.setdefault(substr, 
                                 Variable(set(), set(), set(), set(), set()))
          
          label = row["label"] 
          origin_id = row["origin"]
          getattr(var, label).add(origin_id or id)
          
          ancestor_id = row["ancestor"]
          
          if not pd.isnull(ancestor_id):
               anc_substr = matches.at[int(ancestor_id), "substr"]                    
               var.specifics.add(anc_substr)
               
          descendants_ids = row["descendants"] or []
               
          for desc_id in descendants_ids:
               desc_substr = matches.at[int(desc_id), "substr"]
               var.generals.add(desc_substr)

     return index


def compact_index(index):
     for substr in list(index):
          var = index[substr]
          if ( len(var.generals) == 1 and
               len(var.specifics) == 1 ):
               anc_substr = next(iter(var.specifics))
               desc_substr = next(iter(var.generals))
               
               anc_generals = index[anc_substr].generals
               anc_generals.remove(substr)
               anc_generals.add(desc_substr)
               
               desc_specifics = index[desc_substr].specifics
               desc_specifics.remove(substr)
               desc_specifics.add(anc_substr)

               del index[substr]
     


def write_index(index, outf=None):
     var_ids = {text: id 
                for id, text in enumerate(index.keys())}
     
     sorted_vars = sorted(index.keys(), key=lambda substr: 
                          len(index[substr].change) + 
                          len(index[substr].increase) +
                          len(index[substr].decrease), 
                          reverse=True)
     
     print(header, file=outf)
     
     for text in sorted_vars:
          var = index[text]
          change_n = len(var.change)
          increase_n = len(var.increase)
          decrease_n = len(var.decrease)
          
          change_links = (change_link.format(id=id) 
                          for id in var.change)
          increase_links = (incr_link.format(id=id) 
                            for id in var.increase)
          decrease_links = (decr_link.format(id=id) 
                            for id in var.decrease)
          
          generals = (var_link.format(text=text, 
                                      id=var_ids[text]) 
                      for text in var.generals)
          specifics = (var_link.format(text=text, 
                                       id=var_ids[text]) 
                       for text in var.specifics)
          
          out = table.format(
               var_n = change_n + increase_n + decrease_n,
               var_id = var_ids[text],
               var = text,
               change_n = change_n,
               change_links = "\n".join(change_links),
               increase_n = increase_n,
               increase_links = "\n".join(increase_links),
               decrease_n = decrease_n,
               decrease_links = "\n".join(decrease_links),
               generals = "\n".join(generals),
               specifics = "\n".join(specifics))
    
          print(out, file=outf)
     print(trailer, file=outf)

          
matches = pd.read_pickle("nature_abs_matches_postproc.pkl")           
     
# files with at least two variables
file_counts = matches["file"].value_counts()
files = sorted(file_counts[file_counts > 1].index, reverse=True)
max_files = 1000
files = set(files[:max_files])

trans_matches = pd.read_pickle("nature_abs_matches_postproc_trans.pkl") 

selection = trans_matches["file"].isin(files)
trans_matches = trans_matches[selection]


del matches

index = create_index(trans_matches)
print(len(index))
compact_index(index)
print(len(index))
write_index(index, open("var_index.html", "w"))

pass

