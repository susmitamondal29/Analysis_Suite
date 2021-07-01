#!/usr/bin/env python3
from collections import OrderedDict
from analysis_suite.Variable_Creator.vargetter import VarGetter as vg

# Variables used in Training
usevar = {
    "NJets" :           [vg.num, ("Jets")],
    "NBJets":           [vg.num, ("BJets")],
    "NResolvedTops":    [vg.num, ("ResolvedTops")],
    # "NlooseBJets":      [vg.var, ('BJets/n_loose')],
    # "NtightBJets":      [vg.var, ('BJets/n_tight')],
    # "NlooseMuons":      [vg.num, ('LooseMuon')],
    # "NlooseElectrons":  [vg.num, ('LooseElectron')],
    # "HT":               [vg.var, ('HT')],
    # "HT_b":             [vg.var, ('HT_b')],
    # "Met":              [vg.var, ('Met')],
    # "centrality":       [vg.var, ('Centrality')],
    # "j1Pt":             [vg.pt, ("Jets", 0)],
    # "j2Pt":             [vg.pt, ("Jets", 1)],
    # "j3Pt":             [vg.pt, ("Jets", 2)],
    # "j4Pt":             [vg.pt, ("Jets", 3)],
    # "j5Pt":             [vg.pt, ("Jets", 4)],
    # "j6Pt":             [vg.pt, ("Jets", 5)],
    # "j7Pt":             [vg.pt, ("Jets", 6)],
    # "j8Pt":             [vg.pt, ("Jets", 7)],
    # "b1Pt":             [vg.pt, ("BJets", 0)],
    # "b2Pt":             [vg.pt, ("BJets", 1)],
    # "b3Pt":             [vg.pt, ("BJets", 2)],
    # "b4Pt":             [vg.pt, ("BJets", 3)],
    # "l1Pt": [vg.pt, ("TightLeptons", 0)],
    # "l2Pt": [vg.pt, ("TightLeptons", 1)],
    # "lepMass" : [vg.mass, ("TightLeptons", 0, "TightLeptons", 1)],
    # "lepDR" : [vg.dr, ("TightLeptons", 0, "TightLeptons", 1)],
    # "jetDR" : [vg.dr, ("Jets", 0, "Jets", 1)],
    # "jetMass" : [vg.mass, ("Jets", 0, "Jets", 1)],
    # "LepCos" : [vg.cosDtheta, ("TightLeptons", 0, "TightLeptons", 1)],
    # "JetLep1_Cos" : [vg.cosDtheta, ("TightLeptons", 0, "Jets", 0)],
    # "JetLep2_Cos" : [vg.cosDtheta, ("TightLeptons", 1, "Jets", 0)],
    # "mwT" : [vg.mwT, ('TightLeptons')],

    # "sphericity": "var('Event_variables/Event_sphericity')",
}

cuts = ["l1Pt>25", "l2Pt>20"]

# Input Rootfile
single=True
# Sampels and the groups they are a part of
if single:
    groups = [["Signal", ["ttt", ]],
              ["Background", ["ttw", "ttz", "tth",
                              # "tttt",
                              # "ttXY",
                              # "vvv", "vv", "xg",
                              # "other",
                                  ]]]
else:
    groups = [["Signal", ["ttt"]],
              ["FourTop", ["tttt",]],
              ["Background", ["ttw", "ttz", "tth", "ttXY", "vvv", "vv", "xg","other"
                              ]]]

all_years = ["2016", "2017", "2018"]

# color_by_group = {
#     "ttt": "crimson",
#     "ttw": "darkgreen",
#     "rare": "darkorange",
#     "tth": "slategray",
#     "ttz": "mediumseagreen",
#     "xg": "indigo",
#     "ttXY": "cornflowerblue",
#     # "other": "blue",
#     "tttt": "darkmagenta",
# }
color_by_group = {
    "ttt": "crimson",
    "xg": "indigo",
    "ttz": "mediumseagreen",
    "tth": "slategray",
    "ttw": "darkgreen",
    "ttXY": "cornflowerblue",
    "rare": "darkorange",
    "other": "blue",
    "tttt": "darkmagenta",
}
