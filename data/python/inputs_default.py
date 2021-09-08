#!/usr/bin/env python3
from collections import OrderedDict
from analysis_suite.Variable_Creator.vargetter import VarGetter as vg, Variable
from analysis_suite.Combine.systematics import Systematic

# Variables used in Training
allvar = {
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

# Vars to actually use in training
usevars = {var : allvar[var] for var in [
    "NJets", "NBJets",
    "NResolvedTops",
    "NlooseBJets", "NtightBJets",
    "NlooseMuons", "NlooseElectrons",
    "HT",
    "HT_b",
    "Met",
    "centrality",
    "j1Pt", "j2Pt", "j3Pt", "j4Pt", "j5Pt", "j6Pt", "j7Pt", "j8Pt",
    "b1Pt", "b2Pt", "b3Pt", "b4Pt",
    "l1Pt", "l2Pt",
#    "lepMass", "jetMass",
    "lepDR",
    "jetDR",
    "LepCos", "JetLep1_Cos", "JetLep2_Cos",
    "mwT",
]}




cuts = ["l1Pt>25", "l2Pt>20"]

# Sampels and the groups they are a part of
groups = OrderedDict({
    "Signal": ["ttt"],
    "Background": ["ttw", "ttz", "tth",
                   "ttXY",
                   "vvv", "vv", "xg",
                   "other",],
    "NotTrained": ["tttt",
                   "ttXY",
                   "vvv", "vv", "xg",
                   "other",]
})



all_years = ["2016", "2017", "2018"]
classID = {"Signal": 1, "NotTrained": -1, "Background": 0}


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

systematics = [
    # Systematic("lumi", "lnN").add(1.012, year=2016)
    #                          .add(1.023, year=2017)
    #                          .add(1.025, year=2018),
    Systematic("LHE_muF", "shape").add(1),
    Systematic("LHE_muR", "shape").add(1),
    Systematic("BJet_BTagging", "shape").add(1),
    Systematic("BJet_Eff", "shape").add(1),
    Systematic("Muon_ID", "shape").add(1),
    Systematic("Muon_Iso", "shape").add(1),
    Systematic("Electron_SF", "shape").add(1),
    Systematic("Electron_Susy", "shape").add(1),
    Systematic("Pileup", "shape").add(1),
    Systematic("Top_SF", "shape").add(1),
    # Systematic("Jet_JER", "shape").add(1),
    # Systematic("Jet_JES", "shape").add(1),

    #        ["CMS_norm_tttt", "lnN",  [("tttt", 1.5)]],
    #                ["CMS_norm_ttw", "lnN",   [("ttw", 1.4)]],
    #                ["CMS_norm_ttz", "lnN",   [("ttz", 1.4)]],
    #                ["CMS_norm_tth", "lnN",   [("tth", 1.25)]],
    #                ["CMS_norm_xg", "lnN",    [("xg", 1.5)]],
    #                ["CMS_norm_rare", "lnN",  [("rare", 1.5)]],
]
