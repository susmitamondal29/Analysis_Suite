# -*- coding: utf-8 -*-

info = {
    "BDT.Background" : {
        "Column": "Background",
        "set_xlabel": "$BDT_{Background}$",
        "Binning"     :  [20, 0, 1.],
        "Modify": "1-{}"
    },
    "HT" : {
        "Column": "HT",
        "set_xlabel": "$H_{T}$ (GeV)",
        "Binning"     :  [15, 0, 1200],
    },
    "Met" : {
        "Column": "Met",
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
    "NlooseBJets" : {
        "Column": "NlooseBJets",
        "set_xlabel": "$N_{looseb}$",
        "Binning"     :  [10, 0, 10],
        "Discrete": True,
    },
    "NtightBJets" : {
        "Column": "NtightBJets",
        "set_xlabel": "$N_{tightb}$",
        "Binning"     :  [10, 0, 10],
        "Discrete": True,
    },
    "NTops" : {
        "Column": "NResolvedTops",
        "set_xlabel": "$N_{t}$",
        "Binning"     :  [5, 0, 5],
        "Discrete": True,
    },
    "lep1_pt" : {
        "Column": "l1Pt",
        "set_xlabel": "$p_{T}(j_{1})$",
        "Binning"     :  [30, 0, 500],
    },
    "lep2_pt" : {
        "Column": "l2Pt",
        "set_xlabel": "$p_{T}(j_{2})$",
        "Binning"     :  [30, 0, 500],
    },
}
