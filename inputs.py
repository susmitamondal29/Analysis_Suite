#!/usr/bin/env python3
from collections import OrderedDict

class mva_params:
    # Variables used in Training
    usevar = {
        "NJets": "num('Jets/pt')",
        "NBJets": "num('BJets/pt')",
        # "NlooseBJets": "num_mask('Event_masks/Jet_looseBjetMask')",
        # "NtightBJets": "num_mask('Event_masks/Jet_tightBjetMask')",
        # "NlooseLeps": "num('looseLeptons/Lepton_pt')",
        "HT": "var('HT')",
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
        # "l1Pt": "nth('tightLeptons/Lepton_pt', 0)",
        # "l2Pt": "nth('tightLeptons/Lepton_pt', 1)",
        # "lepMass" : "mass('tightLeptons/Lepton', 0, 'tightLeptons/Lepton', 1)",
        # "lepDR" : "dr('tightLeptons/Lepton', 0, 'tightLeptons/Lepton', 1)",
        # "jetDR" : "dr('Jets/Jet', 0, 'Jets/Jet', 1)",
        # "jetMass" : "mass('Jets/Jet', 0, 'Jets/Jet', 1)",
        # "LepCos" : "cosDtheta('tightLeptons/Lepton', 0, 'tightLeptons/Lepton', 1)",
        # "JetLep1_Cos" : "cosDtheta('tightLeptons/Lepton', 0, 'Jets/Jet', 0)",
        # "JetLep2_Cos" : "cosDtheta('tightLeptons/Lepton', 1, 'Jets/Jet', 0)",
    }

    # Input Rootfile
    single=True
    # Sampels and the groups they are a part of
    if single:
        groups = [["Signal", ["ttt"]],
                  ["Background", ["ttw", "ttz", "tth", "ttXY", "vvv", "vv","xg" "4top2016","other"]]]
    else:
        groups = [["Signal", ["ttt"]],
                  ["FourTop", ["4top2016",]],
                  ["Background", ["ttw", "ttz", "tth", "ttXY", "vvv", "vv", "xg","other"]]] #

class plot_params:
    color_by_group = {
        "ttt": "crimson",
        "ttz": "mediumseagreen",
        "ttw": "darkgreen",
        "tth": "slategray",
        "rare_no3top": "darkorange",
        "ttXY": "cornflowerblue",
        "xg": "indigo",
        #"other": "blue",
        "tttt": "darkmagenta",
    }
