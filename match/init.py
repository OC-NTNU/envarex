#!/usr/bin/env python3

"""
Create empty Tredev instance

This is primarily useful when developing patterns, so the costly step
of parsing the corpus (i.e. creating Nodes instance) does not need to be repeated each time.
"""

# path to parse trees from nature abstracts
parse_dir = "/Users/work/BigData/nature/abstracts/parse"

# variable labels
labels = "change", "increase", "decrease"

# path prefix for Tredev pickled instances 
path_prefix = "nature_abs"


if __name__ == "__main__":
    from tredev import Tredev
    td = Tredev.from_parses(parse_dir, labels) 
    td.save(path_prefix)

