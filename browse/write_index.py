#!/usr/bin/env python

from collections import namedtuple

import pandas as pd


HEADER = """
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


TRAILER = """
</div>
</body>
</html>
"""

TABLE = """
<table class="table">
     <col width="20%" />
     <tr>
          <th scope="row">Variable ({var_n}):</th>
          <td><a id="{var_id}">{var}</a></td>
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

LINK = """
<a href="abstracts.html#{{id}}" target="abstracts" style="color: {color}">
#{{id}}
</a>
"""

CHANGE_LINK = LINK.format(color="green")
INCR_LINK = LINK.format(color="red")
DECR_LINK = LINK.format(color="blue")  


VAR_LINK = '<li><a href="#{id}">{text}</a></li>'


# A Variable tuple represents variable *type*.
# The 'change', 'increase' and 'decrease' sets hold variable *tokens*,
# i.e., unique identifiers of text spans in the text (mentions).
# The 'generals' and 'specifics' sets hold variable *types*,
# i.e., keys of other Variable instances in the index. 
Variable = namedtuple("Variable", 
                      ["id", "change", "increase", "decrease", 
                       "generals", "specifics"])


def create_var_type_index(matches):
    index = {}
    var_type_count = 0

    for var_token_id, row in matches.iterrows():
        substr = row["substr"]

        try:
            var_type = index[substr]
        except KeyError:
            var_type_count += 1
            var_type = Variable(var_type_count, set(), set(), set(), 
                                set(), set())
            index[substr] = var_type

        label = row["label"] 
        # origin is id of first ancestor token, or id of current variable
        # token if it is orginal
        origin_token_id = row["origin"] or var_token_id
        # add id of origin token to appropriate set of variable tokens
        getattr(var_type, label).add(origin_token_id)

        ancestor_token_id = row["ancestor"]

        if not pd.isnull(ancestor_token_id):
            # add substr of ancestor variable token to set of more
            # specific variable types
            anc_substr = matches.at[int(ancestor_token_id), "substr"]                    
            var_type.specifics.add(anc_substr)

        descendants_token_ids = row["descendants"] or []

        # add substr of descendant variable tokens to set of more general
        # variable types
        for desc_id in descendants_token_ids:
            desc_substr = matches.at[int(desc_id), "substr"]
            var_type.generals.add(desc_substr)

    return index


def compact_var_type_index(index):
    # The intuition: if a generalisation does not match more variable
    # tokens, then remove it.
    for substr in list(index):
        var = index[substr]

        # is this a generalized variable?
        if len(var.specifics):

            # are the variable tokens of this variable and each of its
            # specialization identical?
            for spec_substr in var.specifics:
                spec_var = index[spec_substr]

                if (var.change != spec_var.change or
                    var.increase != spec_var.increase or
                    var.decrease != spec_var.decrease):
                    # no!
                    break
            else:
                # yes!

                # for all specializations of the variable
                for spec_substr in var.specifics:
                    spec_var = index[spec_substr]
                    # 1) move all its generalizations to the
                    # generalizations of this specialization
                    spec_var.generals.update(var.generals)
                    # 2) remove it from the the generalisations of this
                    # specialization
                    spec_var.generals.remove(substr)

                # for all generalizations of this variable
                for gen_substr in var.generals:
                    gen_var = index[gen_substr]
                    # 3) move all its specializations to the
                    # specializations of this generalization
                    gen_var.specifics.update(var.specifics)
                    # 4) remove it from the the specializations of this
                    # generalization
                    gen_var.specifics.remove(substr)

                # 5) remove variable from index  
                del index[substr]



def write_var_type_index(index, outf=None):
    # sort variable types according to their total number of variable tokens
    sorted_vars = sorted(index.keys(), key=lambda substr: 
                         len(index[substr].change) + 
                         len(index[substr].increase) +
                         len(index[substr].decrease), 
                         reverse=True)

    print(HEADER, file=outf)

    for text in sorted_vars:
        var = index[text]
        change_n = len(var.change)
        increase_n = len(var.increase)
        decrease_n = len(var.decrease)

        change_links = (CHANGE_LINK.format(id=id) 
                        for id in var.change)
        increase_links = (INCR_LINK.format(id=id) 
                          for id in var.increase)
        decrease_links = (DECR_LINK.format(id=id) 
                          for id in var.decrease)

        generals = (VAR_LINK.format(text=text, 
                                    id=index[text].id) 
                    for text in var.generals)
        specifics = (VAR_LINK.format(text=text, 
                                     id=index[text].id) 
                     for text in var.specifics)

        out = TABLE.format(
            var_n = change_n + increase_n + decrease_n,
            var_id = var.id,
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
    print(TRAILER, file=outf)


def create_var_token_index(trans_matches, var_type_index):
    # create a reverse mapping from variable token id to the corresponding
    # variable type id
    var_token_index = {}

    for token_id, row in trans_matches.iterrows():
        substr = row["substr"]
        try:
            var_type = var_type_index[substr]
        except KeyError:
            # variable type removed during compacting of index
            continue
        var_token_index[token_id] = var_type.id

    return var_token_index




if __name__ == "__main__":
    import pickle
    
    matches = pd.read_pickle("nature_abs_matches_postproc.pkl")  

    # find top-n files with most variables
    top_n = 2500
    file_counts = matches["file"].value_counts()
    parse_fnames = file_counts[:top_n].index
    
    # Surprisingly, when value_counts() is not guaranteed to return files
    # with the count in the same order. Thus taking the top-n files again may
    # result in a different file list! the top-n files will gives files with
    # the same count in a different order. Therefore pickle filenames for use
    # later use in write_abstracts.py
    pickle.dump(parse_fnames, open("parse_fnames.pkl", "wb"))

    del matches    
    
    # select (transformed) variables corresponding to these files
    trans_matches = pd.read_pickle("nature_abs_matches_postproc_trans.pkl") 
    parse_fnames = set(parse_fnames)
    selection = trans_matches["file"].isin(parse_fnames)
    trans_matches = trans_matches[selection]

    var_type_index = create_var_type_index(trans_matches)

    compact_var_type_index(var_type_index)
    
    write_var_type_index(var_type_index, open("var_index.html", "w"))

    var_token_index = create_var_token_index(trans_matches, var_type_index)

    pickle.dump(var_token_index, open("var_token_index.pkl", "wb"))


