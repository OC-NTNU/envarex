#!/usr/bin/env python3

"""
generate postprocessing rules
"""


import pandas as pd

patterns = pd.read_pickle("nature_abs_patterns.pkl")

# idea: if "=d1" in pattern, then generate a deletion rule


rule_template = """
[rule {name}]
targets = {name}
pattern = {pattern}
script = delete d1
"""

with open("postproc_rules.txt", "w") as f:
    for name, pattern in patterns["pattern"].iteritems():
        if "=d1" in pattern:
            f.write(rule_template.format(name=name, pattern=pattern))
            
            
        


