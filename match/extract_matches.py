#!/usr/bin/env python3


from tredev import Tredev

from baleen.extract import Matches

from init import path_prefix, parse_dir


# load data files
td = Tredev.load(path_prefix, parse_dir)

# extract variables, removing duplicates
matches = Matches.from_patterns(td.patterns, td.nodes, parse_dir, drop_duplicates=True)

# save
matches.to_pickle(path_prefix + "_matches.pkl")

