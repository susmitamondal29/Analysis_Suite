#!/usr/bin/env python3
from collections import OrderedDict
from analysis_suite.Combine.systematics import Systematic

pad = True

# Variables used in Training
allvar = {
    "NJets" :           lambda vg : vg.Jets.num(),
    "NBJets":           lambda vg : vg.BJets.num(),
    # "NResolvedTops":    lambda vg : vg.Tops.num(),
    "NlooseBJets":      lambda vg : vg['N_bloose'],
    "NtightBJets":      lambda vg : vg['N_btight'],
    # "NlooseMuons":      lambda vg : vg['N_loose_muon'],
    # "NlooseElectrons":  lambda vg : vg['N_loose_elec'],
    "HT":               lambda vg : vg['HT'],
    "HT_b":             lambda vg : vg['HT_b'],
    "Met":              lambda vg : vg['Met'],
    "centrality":       lambda vg : vg['Centrality'],
    "j1Pt":             lambda vg : vg.Jets['pt', 0, pad],
    "j2Pt":             lambda vg : vg.Jets['pt', 1, pad],
    "j3Pt":             lambda vg : vg.Jets['pt', 2, pad],
    "j4Pt":             lambda vg : vg.Jets['pt', 3, pad],
    "j5Pt":             lambda vg : vg.Jets['pt', 4, pad],
    "j6Pt":             lambda vg : vg.Jets['pt', 5, pad],
    "j7Pt":             lambda vg : vg.Jets['pt', 6, pad],
    "j8Pt":             lambda vg : vg.Jets['pt', 7, pad],
    "b1Pt":             lambda vg : vg.BJets['pt', 0, pad],
    "b2Pt":             lambda vg : vg.BJets['pt', 1, pad],
    "b3Pt":             lambda vg : vg.BJets['pt', 2, pad],
    "b4Pt":             lambda vg : vg.BJets['pt', 3, pad],
    "l1Pt":             lambda vg : vg.TightLepton["pt", 0],
    "l2Pt":             lambda vg : vg.TightLepton["pt", 1],
    "lepMass" :         lambda vg : vg.mass("TightLepton", 0, "TightLepton", 1),
    "lepDR" :           lambda vg : vg.dr("TightLepton", 0, "TightLepton", 1),
    "jetDR" :           lambda vg : vg.dr("Jets", 0, "Jets", 1),
    "jetMass" :         lambda vg : vg.mass("Jets", 0, "Jets", 1),
    "LepCos" :          lambda vg : vg.cosDtheta("TightLepton", 0, "TightLepton", 1),
    "JetLep1_Cos" :     lambda vg : vg.cosDtheta("TightLepton", 0, "Jets", 0),
    "JetLep2_Cos" :     lambda vg : vg.cosDtheta("TightLepton", 1, "Jets", 0),
    "top_mass" :        lambda vg : vg.top_mass("TightLepton", "BJets"),
    # "j1Disc":           Variable(vg.nth, ("Jets", "discriminator", 0)),
    # "j2Disc":           Variable(vg.nth, ("Jets", "discriminator", 1)),
    # "j3Disc":           Variable(vg.nth, ("Jets", "discriminator", 2)),
    # "j4Disc":           Variable(vg.nth, ("Jets", "discriminator", 3)),
    # "j5Disc":           Variable(vg.nth, ("Jets", "discriminator", 4)),
    # "j6Disc":           Variable(vg.nth, ("Jets", "discriminator", 5)),
    # "j7Disc":           Variable(vg.nth, ("Jets", "discriminator", 6)),
    # "j8Disc":           Variable(vg.nth, ("Jets", "discriminator", 7)),

}

# # Vars to actually use in training
# usevars = {var : allvar[var] for var in [
#     # "NJets",
#     "NBJets",
#     # "NResolvedTops",
#     # "NlooseBJets", "NtightBJets",
#     # "NlooseMuons", "NlooseElectrons",
#     # "HT",
#     # "HT_b",
#     # "Met",
#     # "centrality",
#     # "j1Pt", "j2Pt", "j3Pt", "j4Pt", "j5Pt", "j6Pt", "j7Pt", "j8Pt",
#     # "j1Disc", "j2Disc", "j3Disc", "j4Disc", "j5Disc", "j6Disc", "j7Disc", "j8Disc",
#     # # "b1Pt", "b2Pt", "b3Pt", "b4Pt",
#     # "l1Pt", "l2Pt",
#     # #    "lepMass", "jetMass",
#     # "lepDR",
#     # "jetDR",
#     # "LepCos", "JetLep1_Cos", "JetLep2_Cos",
#     # "mwT",
# ]}

cuts = [
    # "NBJets>1",
    # "HT>345",
    "NJets>3",
    "HT_b>130",
    "NlooseBJets>2",
]

# Sampels and the groups they are a part of
groups = OrderedDict({
    "Signal": ["ttt"],
    "Background": ["ttw", "ttz", "tth",
                   "ttXY",
                   "vvv", "vv", "xg",
                   "other",],
    "NotTrained": ["tttt",
                   # "ttXY",
                   # "vvv", "vv", "xg",
                   # "other",
                   ]
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
    # .add(1.023, year=2017)
    # .add(1.025, year=2018),
    # Systematic("LHE_muF", "shape").add(1),
    # Systematic("LHE_muR", "shape").add(1),

    # Systematic("BJet_BTagging", "shape").add(1),
    # Systematic("BJet_Shape_hf", "shape").add(1),
    # Systematic("BJet_Shape_hfstats1", "shape").add(1),
    # Systematic("BJet_Shape_hfstats2", "shape").add(1),
    # Systematic("BJet_Shape_lf", "shape").add(1),
    # Systematic("BJet_Shape_lfstats1", "shape").add(1),
    # Systematic("BJet_Shape_lfstats2", "shape").add(1),
    # Systematic("BJet_Shape_cferr1", "shape").add(1),
    # Systematic("BJet_Shape_cferr2", "shape").add(1),

    # Systematic("BJet_Eff", "shape").add(1),
    # Systematic("Muon_ID", "shape").add(1),
    # Systematic("Muon_Iso", "shape").add(1),
    # Systematic("Electron_SF", "shape").add(1),
    # Systematic("Electron_Susy", "shape").add(1),
    # Systematic("Pileup", "shape").add(1),
    # Systematic("Top_SF", "shape").add(1),
    # Systematic("Jet_JER", "shape").add(1),
    # Systematic("Jet_JES", "shape").add(1),

    #        ["CMS_norm_tttt", "lnN",  [("tttt", 1.5)]],
    #                ["CMS_norm_ttw", "lnN",   [("ttw", 1.4)]],
    #                ["CMS_norm_ttz", "lnN",   [("ttz", 1.4)]],
    #                ["CMS_norm_tth", "lnN",   [("tth", 1.25)]],
    #                ["CMS_norm_xg", "lnN",    [("xg", 1.5)]],
    #                ["CMS_norm_rare", "lnN",  [("rare", 1.5)]],
]
