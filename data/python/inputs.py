#!/usr/bin/env python3
from analysis_suite.Combine.systematics import Systematic

pad = True

# Variables used in Training
allvar = {
    "NJets" :           lambda vg : vg.Jets.num(),
    "NBJets":           lambda vg : vg.BJets.num(),
    "NResolvedTops":    lambda vg : vg.Tops.num(),
    "NlooseBJets":      lambda vg : vg['N_bloose'],
    "NtightBJets":      lambda vg : vg['N_btight'],
    "NlooseMuons":      lambda vg : vg['N_loose_muon'],
    "NlooseElectrons":  lambda vg : vg['N_loose_elec'],
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
    # "top_mass" :        lambda vg : vg.top_mass("TightLepton", "BJets"),
    # "j1Disc":           Variable(vg.nth, ("Jets", "discriminator", 0)),
    # "j2Disc":           Variable(vg.nth, ("Jets", "discriminator", 1)),
    # "j3Disc":           Variable(vg.nth, ("Jets", "discriminator", 2)),
    # "j4Disc":           Variable(vg.nth, ("Jets", "discriminator", 3)),
    # "j5Disc":           Variable(vg.nth, ("Jets", "discriminator", 4)),
    # "j6Disc":           Variable(vg.nth, ("Jets", "discriminator", 5)),
    # "j7Disc":           Variable(vg.nth, ("Jets", "discriminator", 6)),
    # "j8Disc":           Variable(vg.nth, ("Jets", "discriminator", 7)),

}


# Vars to actually use in training
usevars = list(allvar.keys())

tuple_info = {
    'change_name' : {"OS_Charge_MisId" : "charge_misId", "TightFake_Nonprompt": 'nonprompt'},
    'trees' : ["TightFake_Nonprompt", "OS_Charge_MisId", "Signal_Dilepton", 'Signal_Multi'],
    'tree_cuts' : {
        'Signal' : lambda vg : vg['passZVeto'] == 1,
        'CR-ttz' : lambda vg : vg['passZVeto'] == 0,
    },
}

# Samples and the groups they are a part of
groups = {
    "Signal": ["ttt"],
    "Background": [
        "ttw", "ttz", "tth",
        "ttXY",
        "vvv", "vv_inc", "xg",
        "nonprompt", "charge_misId",
        "tttt",
    ],
    "NotTrained": []
}


color_by_group = {
    "ttt": "crimson",

    'nonprompt': 'gray',
    "xg": "indigo",

    "ttw": "olivedrab",
    "tth": "goldenrod",
    "ttz": "steelblue",

    "ttXY": "teal",
    "rare": "deeppink",
    "tttt": "tomato",
    'charge_flip': 'mediumseagreen',
}


systematics = [
    Systematic("lumi", "lnN").add(1.012, year=2016)
                             .add(1.023, year=2017)
                             .add(1.025, year=2018),
    # Systematic("LHE_muF", "shape").add(1),
    # Systematic("LHE_muR", "shape").add(1),
    # Systematic("PDF_unc", "shape").add(1),
    # Systematic("PDF_alphaZ", "shape").add(1),
    # Systematic("PS_ISR", "shape").add(1),
    # Systematic("PS_FSR", "shape").add(1),

    # Systematic("BJet_BTagging", "shape").add(1),
    # Systematic("BJet_Eff", "shape").add(1),
    # Systematic("Muon_Scale", "shape").add(1),
    # Systematic("Electron_Scale", "shape").add(1),
    # Systematic("Pileup", "shape").add(1),
    # # Systematic("Top_SF", "shape").add(1),
    # Systematic("Jet_JER", "shape").add(1),
    # Systematic("Jet_JES", "shape").add(1),
    # Systematic("Jet_PUID", "shape").add(1),

    # Systematic("ChargeMisId_stat", "shape").add(1),
    # Systematic("Nonprompt_Mu_stat", "shape").add(1),
    # Systematic("Nonprompt_El_stat", "shape").add(1),

    # Systematic("BJet_Shape_hf", "shape").add(1),
    # Systematic("BJet_Shape_hfstats1", "shape").add(1),
    # Systematic("BJet_Shape_hfstats2", "shape").add(1),
    # Systematic("BJet_Shape_lf", "shape").add(1),
    # Systematic("BJet_Shape_lfstats1", "shape").add(1),
    # Systematic("BJet_Shape_lfstats2", "shape").add(1),
    # Systematic("BJet_Shape_cferr1", "shape").add(1),
    # Systematic("BJet_Shape_cferr2", "shape").add(1),

    # Systematic("CMS_norm_tttt", "lnN").add(1.5, groups="tttt"),
    # Systematic("CMS_norm_ttw", "lnN").add(1.5, groups="ttw"),
    # Systematic("CMS_norm_ttz", "lnN").add(1.5, groups="ttz"),
    # Systematic("CMS_norm_tth", "lnN").add(1.5, groups="tth"),
    # Systematic("CMS_norm_xg", "lnN").add(1.5, groups="xg"),
    # Systematic("CMS_norm_rare", "lnN").add(1.5, groups="rare"),
]

# Variables needed in code for things to work
assert "allvar" in locals()
assert 'usevars' in locals()
assert 'tuple_info' in locals()
assert 'groups' in locals()
assert 'color_by_group' in locals()
assert "systematics" in locals()
