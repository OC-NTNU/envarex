#!/usr/bin/env python3

"""
Apply postprocessing rules
"""


import pandas as pd

from baleen.postproc import post_process


matches = pd.read_pickle("nature_abs_matches.pkl")

post_process(matches, "postproc_rules.txt")

pd.to_pickle(matches, "nature_abs_matches_postproc.pkl")
