#!/usr/bin/env python3
from collections import OrderedDict

class mva_params:
    # Variables used in Training
    usevar = {
        "NJets": "num('Jets/pt')",
        "NBJets": "num('BJets/pt')",
        # "NlooseBJets": "var('BJets/n_loose')",
        # "NtightBJets": "var('BJets/n_tight')",
        "NResolvedTops": "num('ResolvedTops/pt')",
        # "NlooseLeps": "num('looseLeptons/Lepton_pt')",
        "HT": "var('HT')",
        "HT_b": "var('HT_b')",
        "Met": "var('Met')",
        "centrality": "var('Centrality')",
        # "sphericity": "var('Event_variables/Event_sphericity')",
        "j1Pt": "nth('Jets/pt', 0)",
        "j2Pt": "nth('Jets/pt', 1)",
        "j3Pt": "nth('Jets/pt', 2)",
        "j4Pt": "nth('Jets/pt', 3)",
        "j5Pt": "nth('Jets/pt', 4)",
        "j6Pt": "nth('Jets/pt', 5)",
        "j7Pt": "nth('Jets/pt', 6)",
        "j8Pt": "nth('Jets/pt', 7)",
        "b1Pt": "nth('BJets/pt', 0)",
        "b2Pt": "nth('BJets/pt', 1)",
        "b3Pt": "nth('BJets/pt', 2)",
        "b4Pt": "nth('BJets/pt', 3)",
        "l1Pt": "nth('TightLeptons/pt', 0)",
        "l2Pt": "nth('TightLeptons/pt', 1)",
        "lepMass" : "mass('TightLeptons', 0, 'TightLeptons', 1)",
        "lepDR" : "dr('TightLeptons', 0, 'TightLeptons', 1)",
        "jetDR" : "dr('Jets', 0, 'Jets', 1)",
        "jetMass" : "mass('Jets', 0, 'Jets', 1)",
        "LepCos" : "cosDtheta('TightLeptons', 0, 'TightLeptons', 1)",
        "JetLep1_Cos" : "cosDtheta('TightLeptons', 0, 'Jets', 0)",
        "JetLep2_Cos" : "cosDtheta('TightLeptons', 1, 'Jets', 0)",
        "mwT" : "mwT('TightLeptons')",
    }

    cuts = ["l1Pt>25", "l2Pt>20"]

    # Input Rootfile
    single=True
    # Sampels and the groups they are a part of
    if single:
        groups = [["Signal", ["ttt", ]],
                  ["Background", ["ttw", # "tttt",
                                  "ttz", "tth", "ttXY",
                                  # "vvv", "vv", "xg",
                                  # "other",
                                  ]]]
    else:
        groups = [["Signal", ["ttt"]],
                  ["FourTop", ["tttt",]],
                  ["Background", ["ttw", "ttz", "tth", "ttXY", "vvv", "vv", "xg","other"
                                  ]]] #

class plot_params:
    lumi = {
        "2016" : 35.9,
        "2017" : 41.5,
        "2018" : 59.6,
        "all" : 137.0,
    }
    color_by_group = {
        "ttt": "crimson",
        "ttw": "darkgreen",
        "rare": "darkorange",
        "tth": "slategray",
        "ttz": "mediumseagreen",
        "xg": "indigo",
        "ttXY": "cornflowerblue",
        # "other": "blue",
        "tttt": "darkmagenta",
    }
