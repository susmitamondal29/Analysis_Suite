# -*- coding: utf-8 -*-

info = {
    "Signal" : {
        "Column": "Signal",
        "Label": "$BDT_{Signal}$",
        "Binning"     :  [20, 0, 1.],
    },

    "NJets" : {
        "Column": "NJets",
        "Label": "$N_{j}$",
        "Binning"     :  [10, 0, 10],
        "Discrete": True,
    },
    "NBJets" : {
        "Column": "NBJets",
        "Label": "$N_{b}$",
        "Binning"     :  [6, 0, 6],
        "Discrete": True,
    },
    "NBJets_withCuts" : {
        "Column": "NBJets",
        "Label": "$N_{b}$",
        "Binning"     :  [6, 0, 6],
        "Discrete": True,
        "Cuts" : ["Signal>0.76"]
    },

    "NResolvedTops" : {
        "Column": "NResolvedTops",
        "Label": "$N_{t}$",
        "Binning"     :  [5, 0, 5],
        "Discrete": True,
    },

    "NlooseBJets" : {
        "Column": "NlooseBJets",
        "Label": "$N_{looseb}$",
        "Binning"     :  [10, 0, 10],
        "Discrete": True,
    },
    "NtightBJets" : {
        "Column": "NtightBJets",
        "Label": "$N_{tightb}$",
        "Binning"     :  [6, 0, 6],
        "Discrete": True,
    },

    "NlooseMuons" : {
        "Column": "NlooseMuons",
        "Label": "$N_{loose}(\mu)$",
        "Binning"     :  [4, 0, 4],
        "Discrete": True,
    },
    "NlooseElectrons" : {
        "Column": "NlooseElectrons",
        "Label": "$N_{loose}(e)$",
        "Binning"     :  [4, 0, 4],
        "Discrete": True,
    },

    "HT" : {
        "Column": "HT",
        "Label": "$H_{T}$ (GeV)",
        "Binning"     :  [15, 0, 1500],
    },
    "HT_b" : {
        "Column": "HT_b",
        "Label": "$H_{T}(b)$ (GeV)",
        "Binning"     :  [15, 0, 1200],
    },

    "Met" : {
        "Column": "Met",
        "Label": "$p_{T}^{miss}$ (GeV)",
        "Binning"     :  [20, 0, 500],
    },

    "centrality" : {
        "Column": "centrality",
        "Label": "$centrality$",
        "Binning"     :  [20, 0, 1.],
    },

    "j1Pt" : {
        "Column": "j1Pt",
        "Label": "$p_{T}(j_{1})$",
        "Binning"     :  [30, 0, 650],
    },
    "j2Pt" : {
        "Column": "j2Pt",
        "Label": "$p_{T}(j_{2})$",
        "Binning"     :  [30, 0, 500],
    },
    "j3Pt" : {
        "Column": "j3Pt",
        "Label": "$p_{T}(j_{3})$",
        "Binning"     :  [20, 0, 300],
    },
    "j4Pt" : {
        "Column": "j4Pt",
        "Label": "$p_{T}(j_{4})$",
        "Binning"     :  [20, 0, 250],
    },
    "j5Pt" : {
        "Column": "j5Pt",
        "Label": "$p_{T}(j_{5})$",
        "Binning"     :  [15, 0, 150],
    },
    "j6Pt" : {
        "Column": "j6Pt",
        "Label": "$p_{T}(j_{6})$",
        "Binning"     :  [15, 0, 150],
    },
    "j7Pt" : {
        "Column": "j7Pt",
        "Label": "$p_{T}(j_{7})$",
        "Binning"     :  [15, 0, 150],
    },
    "j8Pt" : {
        "Column": "j8Pt",
        "Label": "$p_{T}(j_{8})$",
        "Binning"     :  [15, 0, 100],
    },

    "b1Pt" : {
        "Column": "b1Pt",
        "Label": "$p_{T}(b_{1})$",
        "Binning"     :  [30, 0, 500],
    },
    "b2Pt" : {
        "Column": "b2Pt",
        "Label": "$p_{T}(b_{2})$",
        "Binning"     :  [30, 0, 300],
    },
    "b3Pt" : {
        "Column": "b3Pt",
        "Label": "$p_{T}(b_{3})$",
        "Binning"     :  [30, 0, 200],
    },
    "b4Pt" : {
        "Column": "b4Pt",
        "Label": "$p_{T}(b_{4})$",
        "Binning"     :  [30, 0, 100],
    },

    "l1Pt" : {
        "Column": "l1Pt",
        "Label": "$p_{T}(\ell_{1})$",
        "Binning"     :  [30, 0, 500],
    },
    "l2Pt" : {
        "Column": "l2Pt",
        "Label": "$p_{T}(\ell_{2})$",
        "Binning"     :  [20, 0, 250],
    },

    "lepMass" : {
        "Column": "lepMass",
        "Label": "$m(\ell_{1}, \ell_{2})$",
        "Binning"     :  [30, 0, 1500],
    },

    "lepDR" : {
        "Column": "lepDR",
        "Label": "$\Delta R(\ell_{1}, \ell_{2})$",
        "Binning"     :  [30, 0, 6.],
    },
    "jetDR" : {
        "Column": "lepDR",
        "Label": "$\Delta R(j_{1}, j_{2})$",
        "Binning"     :  [30, 0, 6.],
    },
    "jetMass" : {
        "Column": "jetMass",
        "Label": "$m(j_{1}, j_{2})$",
        "Binning"     :  [30, 0, 1500],
    },

    "LepCos" : {
        "Column": "LepCos",
        "Label": "$\cos(\Delta\phi(\ell_{1}, \ell_{2}))$",
        "Binning"     :  [20, -1, 1],
    },
    "JetLep1_Cos"  : {
        "Column": "JetLep1_Cos",
        "Label": "$\cos(\Delta\phi(j_{1}, \ell_{1}))$",
        "Binning"     :  [20, -1, 1],
    },
    "JetLep2_Cos"  : {
        "Column": "JetLep2_Cos",
        "Label": "$\cos(\Delta\phi(j_{1}, \ell_{2}))$",
        "Binning"     :  [20, -1, 1],
    },
    "mwT" : {
        "Column": "mwT",
        "Label": "$m(W_{T})$",
        "Binning"     :  [30, 0, 300],
    },

}
