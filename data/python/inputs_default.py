#!/usr/bin/env python3
from collections import OrderedDict
from analysis_suite.Variable_Creator.vargetter import VarGetter as vg, Variable


# Variables used in Training
usevar = {
    "NJets" :           Variable(vg.num, "Jets"),
    "NBJets":           Variable(vg.num, "BJets"),
    "NResolvedTops":    Variable(vg.num, "ResolvedTops"),
    "NlooseBJets":      Variable(vg.var, 'BJets/n_loose'),
    "NtightBJets":      Variable(vg.var, 'BJets/n_tight'),
    "NlooseMuons":      Variable(vg.num, 'LooseMuon'),
    "NlooseElectrons":  Variable(vg.num, 'LooseElectron'),
    "HT":               Variable(vg.var, 'HT'),
    "HT_b":             Variable(vg.var, 'HT_b'),
    "Met":              Variable(vg.var, 'Met'),
    "centrality":       Variable(vg.var, 'Centrality'),
    "j1Pt":             Variable(vg.pt, ("Jets", 0)),
    "j2Pt":             Variable(vg.pt, ("Jets", 1)),
    "j3Pt":             Variable(vg.pt, ("Jets", 2)),
    "j4Pt":             Variable(vg.pt, ("Jets", 3)),
    "j5Pt":             Variable(vg.pt, ("Jets", 4)),
    "j6Pt":             Variable(vg.pt, ("Jets", 5)),
    "j7Pt":             Variable(vg.pt, ("Jets", 6)),
    "j8Pt":             Variable(vg.pt, ("Jets", 7)),
    "b1Pt":             Variable(vg.pt, ("BJets", 0)),
    "b2Pt":             Variable(vg.pt, ("BJets", 1)),
    "b3Pt":             Variable(vg.pt, ("BJets", 2)),
    "b4Pt":             Variable(vg.pt, ("BJets", 3)),
    "l1Pt":             Variable(vg.pt, ("TightLeptons", 0)),
    "l2Pt":             Variable(vg.pt, ("TightLeptons", 1)),
    "lepMass" :         Variable(vg.mass, ("TightLeptons", 0, "TightLeptons", 1)),
    "lepDR" :           Variable(vg.dr, ("TightLeptons", 0, "TightLeptons", 1)),
    "jetDR" :           Variable(vg.dr, ("Jets", 0, "Jets", 1)),
    "jetMass" :         Variable(vg.mass, ("Jets", 0, "Jets", 1)),
    "LepCos" :          Variable(vg.cosDtheta, ("TightLeptons", 0, "TightLeptons", 1)),
    "JetLep1_Cos" :     Variable(vg.cosDtheta, ("TightLeptons", 0, "Jets", 0)),
    "JetLep2_Cos" :     Variable(vg.cosDtheta, ("TightLeptons", 1, "Jets", 0)),
    "mwT" :             Variable(vg.mwT, 'TightLeptons'),

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
