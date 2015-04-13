#!/usr/bin/env python3

"""
generate patterns by instantiating patterns with verbs/nouns
"""

import pandas as pd
from tredev import Tredev

from init import parse_dir, labels, path_prefix

# use existing Nodes instance to save time
nodes = pd.read_pickle(path_prefix + "_nodes.pkl")
td = Tredev.from_nodes(parse_dir, labels, nodes)


#-----------------------------------------------------------------------------    
# GENERAL PATTERNS
#-----------------------------------------------------------------------------  

verb_patterns = { 
    "SUBJ"  : "NP > (S <+(S|VP) (VP <<# /{}/ !< NP))",
    "OBJ"   : "NP > (VP <<# /{}/ )",
    "ATTR1" : "NP < (VBN|VBD|VBG=d1 < /{}/) !$. PP",
    "ATTR2" : "NP < (NP < (VBN|VBD|VBG=d1 < /{}/) $. PP)" 
}


noun_patterns = {
    "NOM1" : "NP <- (/NN/=d1 < /{}/ $ /NN/ )  !$. PP",
    "NOM2" : "NP < (NP <- (/NN/=d1 < /{}/ $ /NN/ )  $. PP)"
}


pcomp_pattern = "NP > (PP <<# ({}) $, (NP <<# /{}/))"



def generate_patterns(verbs, verb_patterns, nouns,
                      noun_patterns, pcomp_pattern):

    change_verb_patterns = [ (name + "_" + verb, tree_pat.format(verb_pat))
                             for name, tree_pat in verb_patterns.items()
                             for verb, verb_pat in verbs.items() ]

    change_nominal_patterns = [ (name + "_" + noun, tree_pat.format(noun_pat))
                                for name, tree_pat in noun_patterns.items()
                                for noun, noun_pat in nouns.items() ]

    change_pcomp_patterns = [ ("PCOMP_" + name, 
                               pcomp_pattern.format(prep, noun)) 
                              for name, (noun, prep) in nouns.items()]

    return ( change_verb_patterns + 
             change_nominal_patterns +
             change_pcomp_patterns )


#-----------------------------------------------------------------------------    
# CHANGE
#-----------------------------------------------------------------------------  

change_verbs = {
    "adapt"     : "^[Aa]dapt(s|ed|ing)?$",
    "adjust"    : "^[Aa]djust(s|ed|ing)?$",
    "alter"     : "^[Aa]lter(s|ed|ing)?$",
    "change"    : "^[Cc]hang(e|es|ed|ing)$",
    "evolve"    : "^[Ev]olv(e|es|ed|ing)$",
    "fluctuate" : "^[Ff]luctuat(e|es|ed|ing)$",
    "modify"    : "^[Mm]odif(y|ies|ied|ying)$",
    "modulate"  : "^[Mm]odulat(e|es|ed|ing)$",
    "mutate"    : "^[Mm]utat(e|es|ed|ing)$",
    "shift"     : "^[Ss]hift(s|ed|ing)?$",
    "transform" : "^[Tt]ransform(s|ed|ing)?$",
    "vary"      : "^[Vv]ar(y|ies|ied|ying)$",
}

change_nouns = {
    "adapt"     : ( "^[Aa]daptations?$", "of" ), 
    "adjust"    : ( "^[Aa]djustments?$", "in|of" ), 
    "alter"     : ( "^[Aa]lterations?$", "in|of|to" ), 
    "change"    : ( "^[Cc]hange(s)?", "in|of|to" ), 
    "evolve"    : ( "^[Ee]volution?$", "in|of" ), 
    "fluctuate" : ( "^[Ff]luctuations?$", "in|of" ), 
    "modify"    : ( "^[Mm]odification(s)?$", "in|of|to" ), 
    "modulate"  : ( "^[Mm]odulations?$", "in|of" ), 
    "mutate"    : ( "^[Mm]utations?$", "in|of" ), 
    "shift"     : ( "^[Ss]hifts?$", "in|of" ), 
    "transform" : ( "^[Tt]ransformations?$", "of" ), 
    "vary"      : ( "^[Vv]aria(tions?|nces?|bility|)$", "in|of" ), 
}


change_patterns = generate_patterns(change_verbs, verb_patterns,
                                    change_nouns, noun_patterns, 
                                    pcomp_pattern)

for name, pattern in change_patterns:
    td.add(name, pattern, "change", score=False)
    
   
    
#-----------------------------------------------------------------------------    
# INCREASE
#-----------------------------------------------------------------------------    
        
increase_verbs = {
    "add" : "^[Aa]dd(s|ed|ing)?$", 
    "accumulate" : "^[Aa]ccumulat(e|es|ed|ing)$", 
    "augment" : "^[Au]gment(s|ed|ing)?$", 
    "boost" : "^[Bb]oost(s|ed|ing)?$", 
    "double" : "^[Dd]oubl(e|es|ed|ing)$",
    "elevate" : "^[Ee]levat(e|es|ed|ing)$",
    "enhance" : "^[Ee]nhanc(e|es|ed|ing)$",
    "enlarge" : "^[Ee]nlarg(e|es|ed|ing)$",
    "expand" : "^[Ee]xpand(s|ed|ing)?$",
    "gain" : "^[Gg]ain(s|ed|ing)?$",
    "grow" : "^[Gg](row|grows|rew|rown|rowing)$",
    "heighten" : "^[Hh]eighten(s|ed|ing)?$",
    "increase" : "^[Ii]ncreas(e|es|ed|ing)$",
    "intensify" : "^[Ii]ntensif(y|ies|ied|ying)$",
    "lengthen" : "^[Ll]nengthen(s|ed|ing)?$",
    "prolong" : "^[Pp]rolong(s|ed|ing)?$",
    "raise" : "^[Rr]ais(e|es|ed|ing)$",
    "rise" : "^[Rr](ise|ose|isen|ising)$",
    "triple" : "^[Tt]ripl(e|es|ed|ing)$",
    "strengthen" : "^[Ss]trengthen(s|ed|ing)?$",
}    

# Rejected because of low precison:
# * advance
# * amplify
# * build
# * deepen
# * develop
# * extend
# * gather
# * import
# * increment
# * inflate
# * multiply
# * magnify
# * progress
# * reinforce
# * suplement
# * swell
# * widen

# TODO:
# * build up


increase_nouns = {
    "add"        : ( "^[Aa]dditions?$", "of"),
    "accumulate" : ( "^[Aa]ccumulations?$", "of"),
    "augment"    : ( "^[Aa]ugmentations?$", "of"),
    "boost"      : ( "^[Bb]oosts?$", "in|of"),
    "double"     : ( "^[Dd]oubles?$", "in"),
    "enhance"    : ( "^[Ee]nhancements?$", "in|of"),
    "enlarge"    : ( "^[Ee]nlargements?$", "of"),
    "expand"     : ( "^[Ee]xpansions?$", "in|of"),
    "gain"       : ( "^[Gg]ains?$", "in|of"),
    "grow"       : ( "^[Gg]rowths?$", "of"),
    "increase"   : ( "^[Ii]ncreases?$", "in|of"),
    "prolong"    : ( "^[Pp]rolongations?$", "of"),
    "raise"      : ( "^[Rr]aises?$", "in"),
    "rise"       : ( "^[Rr]ises?$", "in|of"),
    }

# TODO:
# other increase nouns?


increase_patterns = generate_patterns(increase_verbs, verb_patterns,
                                      increase_nouns, noun_patterns, 
                                      pcomp_pattern)

for name, pattern in increase_patterns:
    td.add(name, pattern, "increase", score=False)


#-----------------------------------------------------------------------------    
# INCREASE
#-----------------------------------------------------------------------------    


decrease_verbs = {
    "cut"      : "^[Cc]ut(s|ting)?$",
    "decrease" : "^[Dd]ecreas(e|es|ed|ing)$",
    "curb"     : "^[Cc]urb(s|ed|ing)?$",
    "decline"  : "^[Dd]eclin(e|es|ed|ing)$",
    "deplete"  : "^[Dd]eplet(e|es|ed|ing)$",
    "diminish" : "^[Dd]iminish(es|ed|ing)?$",
    "drop"     : "^[Dd]rop(s|ped|ping)$",
    "exhaust"  : "^[Ee]xhaust(s|ed|ing)?$",
    "export"   : "^[Ee]xport(s|ed|ing)?$",
    "fall"     : "^[Ff](alls|ell|alling)$",
    "lessen"   : "^[L]essen(s|ed|ing)?$",
    "limit"    : "^[L]imit(s|ed|ing)?$",
    "lower"    : "^[Ll]ower(s|ed|ing)?$",
    "minimize" : "^[Mm]inimiz(e|es|ed|ing)$", 
    "mitigate" : "^[Mm]itigat(e|es|ed|ing)$", 
    "recede"   : "^[Rr]eced(e|es|ed|ing)$",
    "reduce"   : "^[Rr]educ(e|es|ed|ing)$",
    "shrink"   : "^[Ss](hrinks?|hrank|hrunk|hrunken|hrinking)?$",
}
    

decrease_nouns = {
    "decrease" : ( "^[Dd]ecreases?$", "in|of"),
    "decline"  : ( "^[Dd]eclines?$", "in|of"),
    "deplete"  : ( "^[Dd]epletions?$", "of"),
    "drop"     : ( "^[Dd]rops?$", "of"),
    "exhaust"  : ( "^[Ee]xhaustions?$", "of"),
    "export"   : ( "^[Ee]xports?$", "of"),
    "fall"     : ( "^[Ff]all$", "in"),
    "limit"    : ( "^[Ll]imitations$", "of"),
    "loss"     : ( "^[Ll]oss(es)?$", "of"),
    "mitigate" : ( "^[Mm]itigations?$", "of"),
    "reduce"   : ( "^[Rr]eductions?$", "in|of"),
    "shrink"   : ( "^[Ss]krinkages?$", "in|of"),
}    
    
    


decrease_patterns = generate_patterns(decrease_verbs, verb_patterns,
                                      decrease_nouns, noun_patterns, 
                                      pcomp_pattern)

for name, pattern in decrease_patterns:
    td.add(name, pattern, "decrease", score=False)    

    
td.save(path_prefix)

    
    
# TODO: comparative adjectives/adverbs
# more - less/fewer
# greater/larger/bigger/wider/broader/taller/wider - smaller/narrower/shorter
# longer - shorter/briefer
# higher - lower
# better - worse
# earlier/sooner - later
# drier - wetter
# warmer/hotter - cooler
# faster - slower
# longer - shorter
# further - closer
# deeper - shallower
# stronger - weaker
# older - younger
# richer - poorer
# heavier - lighter
# harder - softer
# thicker - thinner
# brighter - dimmer
# lighter - darker
# easier - harder
# younger - older/elder
# newer - older
# smoother - rougher
# thicker - leaner
# softer - firmer
# tigther - looser
# fatter - leaner






