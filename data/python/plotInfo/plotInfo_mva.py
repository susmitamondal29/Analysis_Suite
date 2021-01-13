# -*- coding: utf-8 -*-

     # "NlooseBJets": "num_mask('Event_masks/Jet_looseBjetMask')",
    # "NtightBJets": "num_mask('Event_masks/Jet_tightBjetMask')",    "centrality": "var('Event_variables/Event_centrality')",
    # "sphericity": "var('Event_variables/Event_sphericity')",
    # "jetDR" : "dr('Jets/Jet', 0, 'Jets/Jet', 1)",
    # "jetMass" : "mass('Jets/Jet', 0, 'Jets/Jet', 1)",


info = {
    # "BDT.Background" : {
    #     "Column": "BDT.Background",
    #     "set_xlabel": "$BDT_{Background}$",
    #     "Binning"     :  [20, 0, 1.],
    #     "Modify": "1-{}"
    # },
    "HT" : {
        "Column": "HT",
        "set_xlabel": "$H_{T}$ (GeV)",
        "Binning"     :  [15, 0, 1200],
    },
    "Met" : {
        "Column": "MET",
        "set_xlabel": "$p_{T}^{miss}$ (GeV)",
        "Binning"     :  [20, 0, 500],
    },
    "NJets" : {
        "Column": "NJets",
        "set_xlabel": "$N_{j}$",
        "Binning"     :  [10, 0, 10],
        "Discrete": True,
    },
    "NBJets" : {
        "Column": "NBJets",
        "set_xlabel": "$N_{b}$",
        "Binning"     :  [10, 0, 10],
        "Discrete": True,
    },
    # "NlooseBJets" : {
    #     "Column": "NlooseBJets",
    #     "set_xlabel": "$N_{looseb}$",
    #     "Binning"     :  [10, 0, 10],
    #     "Discrete": True,
    # },
    # "NtightBJets" : {
    #     "Column": "NtightBJets",
    #     "set_xlabel": "$N_{tightb}$",
    #     "Binning"     :  [10, 0, 10],
    #     "Discrete": True,
    # },
    # "Jet1_pt" : {
    #     "Column": "j1Pt",
    #     "set_xlabel": "$p_{T}(j_{1})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "Jet2_pt" : {
    #     "Column": "j2Pt",
    #     "set_xlabel": "$p_{T}(j_{2})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "Jet3_pt" : {
    #     "Column": "j3Pt",
    #     "set_xlabel": "$p_{T}(j_{3})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "Jet4_pt" : {
    #     "Column": "j4Pt",
    #     "set_xlabel": "$p_{T}(j_{4})$",
    #     "Binning"     :  [30, 0, 300],
    # },
    # "Jet5_pt" : {
    #     "Column": "j5Pt",
    #     "set_xlabel": "$p_{T}(j_{5})$",
    #     "Binning"     :  [30, 0, 200],
    # },
    # "Jet6_pt" : {
    #     "Column": "j6Pt",
    #     "set_xlabel": "$p_{T}(j_{6})$",
    #     "Binning"     :  [30, 0, 150],
    # },
    # "Jet7_pt" : {
    #     "Column": "j7Pt",
    #     "set_xlabel": "$p_{T}(j_{7})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "Jet8_pt" : {
    #     "Column": "j8Pt",
    #     "set_xlabel": "$p_{T}(j_{8})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "BJet1_pt" : {
    #     "Column": "b1Pt",
    #     "set_xlabel": "$p_{T}(b_{1})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "BJet2_pt" : {
    #     "Column": "b2Pt",
    #     "set_xlabel": "$p_{T}(b_{2})$",
    #     "Binning"     :  [30, 0, 500],
    # },
    # "BJet3_pt" : {
    #     "Column": "b3Pt",
    #     "set_xlabel": "$p_{T}(b_{3})$",
    #     "Binning"     :  [30, 0, 250],
    # },
    # "BJet4_pt" : {
    #     "Column": "b4Pt",
    #     "set_xlabel": "$p_{T}(b_{4})$",
    #     "Binning"     :  [30, 0, 500],
    # },
}
