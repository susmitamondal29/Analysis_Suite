#!/usr/bin/env python3

info = {
    'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8': {
        'alias': "DYm10-50",
        "cross_section" : 18610,
        "Source of cross section" : "AN2018-062",
    },
    'DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8': {
        'alias': "DYm50",
        "cross_section" : 6020.85,
        "Source of cross section" : "AN2018-062",
    },
    'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8': {
        'alias': "ggh2zz",
        "cross_section" :  0.01181,
        "Source of cross section" : "AN2018-062",
    },
    'ST_tWll_5f_LO_TuneCP5_PSweights_13TeV-madgraph-pythia8': {
        'alias': "st_twll",
        "cross_section" : 0.01123,
        "Source of cross section" : "AN2018-062",
    },
    'TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8': {
        'alias': "tg",
        "cross_section" : 2.967,
        "Source of cross section" : "AN2018-062",
    },
    'TTGamma_Dilept_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttg_dilep",
        "cross_section" : 0.632,
        "Source of cross section" : "AN2018-062",
    },
    'TTGamma_Hadronic_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttg_hadronic",
        "cross_section" : 0.794,
        "Source of cross section" : "MCM",
    },
    'TTGamma_SingleLept_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttg_singleLept",
        "cross_section" : 5.048,
        "Source of cross section" : "MCM",
    },
    'TTHH_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "tthh",
        "cross_section" : 0.000757,
        "Source of cross section" : "AN2018-062",
    },
    'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8': {
        'alias': "tth",
        "cross_section" : 0.2710,
        "Source of cross section" : "AN2018-062",
    },
    'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8': {
        'alias': "ttjet",
        "cross_section" : 831.762,
        "Source of cross section" : "AN2018-062",
    },
    'TTTJ_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "tttj",
        "cross_section" : 0.000474,
        "Source of cross section" : "AN2018-062",
    },
    'TTTT_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "tttt",
        "cross_section" : 0.008213,
        "Source of cross section" : "MCM",
    },
    'TT_TuneCH3_13TeV-powheg-herwig7': {
        'alias': "ttbar",
        "cross_section" : 689.7,
        "Source of cross section" : "MCM",
    },
    'TTTW_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "tttw",
        "cross_section" : 0.000788,
        "Source of cross section" : "AN2018-062",
    },
    'TTWH_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttwh",
        "cross_section" : 0.001582,
        "Source of cross section" : "AN2018-062",
    },
    'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8': {
        'alias': "ttw",
        "cross_section" : 0.2043,
        "Source of cross section" : "AN2018-062",
    },
    'TTWW_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttww",
        "cross_section" : 0.01150,
        "Source of cross section" : "AN2018-062",
    },
    'TTWZ_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttwz",
        "cross_section" : 0.003884,
        "Source of cross section" : "AN2018-062",
    },
    'TTZH_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttzh",
        "cross_section" : 0.001535,
        "Source of cross section" : "AN2018-062",
    },
    'TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "ttz",
        "cross_section" : 0.0493,
        "Source of cross section" : "AN2018-062",
    },
    'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "ttz_m1-10",
        "cross_section" : 0.2529,
        "Source of cross section" : "AN2018-062",
    },
    'TTZZ_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "ttzz",
        "cross_section" : 0.001982,
        "Source of cross section" : "AN2018-062",
    },
    'tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "tzq",
        "cross_section" : 0.0736,
        "Source of cross section" : "MCM",
    },
    'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8': {
        'alias': "vh2nonbb",
        "cross_section" : 0.9561,
        "Source of cross section" : "AN2018-062",
    },
    'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8': {
        'alias': "wg",
        "cross_section" : 405.271,
        "Source of cross section" : "AN2018-062",
    },
    'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8': {
        'alias': "wjets",
        "cross_section" : 61334.9,
        "Source of cross section" : "AN2018-062",
    },
    'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8': {
        'alias': "wpwpjj_ewk",
        "cross_section" : 0.03711,
        "Source of cross section" : "AN2018-062",
    },
    'WWG_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "wwg",
        "cross_section" : 0.2147,
        "Source of cross section" : "AN2018-062",
    },
    'WWTo2L2Nu_DoubleScattering_13TeV-pythia8': {
        'alias': "ww_doubleScatter",
        "cross_section" : 0.16975,
        "Source of cross section" : "AN2018-062",
    },
    'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "www",
        "cross_section" : 0.2086,
        "Source of cross section" : "AN2018-062",
    },
    'WWZ_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "wwz",
        "cross_section" : 0.1651,
        "Source of cross section" : "MCM",
    },
    'WZG_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "wzg",
        "cross_section" : 0.04123,
        "Source of cross section" : "AN2018-062",
    },
    'WZTo3LNu_TuneCP5_13TeV-powheg-pythia8': {
        'alias': "wz2lnu_powheg",
        "cross_section" : 4.4297,
        "Source of cross section" : "AN2018-062",
    },
    'WZZ_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "wzz",
        "cross_section" : 0.05565,
        "Source of cross section" : "AN2018-062",
    },
    'ZGTo2LG_PtG-130_TuneCP5_13TeV-amcatnloFXFX-pythia8': {
        'alias': "zg",
        "cross_section" : 0.166,
        "Source of cross section" : "MCM",
    },
    'ZZTo4L_TuneCP5_13TeV_powheg_pythia8': {
        'alias': "zz4l",
        "cross_section" : 1.256,
        "Source of cross section" : "AN2018-062",
    },
    'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8': {
        'alias': "zzz",
        "cross_section" : 0.01398,
        "Source of cross section" : "AN2018-062",
    },



    




}
