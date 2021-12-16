#!/usr/bin/env python3

info = {
    # TTT
    "TTTJ" : {
        "cross_section" : 0.0004741,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTTJ_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTTJ_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTTJ_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTTW" : {
        "cross_section" : 0.000788,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTTW_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTTW_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTTW_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # TTTT
    "TTTT" : {
        "cross_section" : 0.001197,
        "Source of cross section" : "MCM",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'TTTT_TuneCUETP8M2T4_13TeV-amcatnlo-pythia8',
            2017: 'TTTT_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'TTTT_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },

    # TTXY
    "TTZH" : {
        "cross_section" : 0.001535,
        "Source of cross section" : "arXiv:1610.07922",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTZH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTZH_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTZH_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTHH" : {
        "cross_section" : 0.000757,
        "Source of cross section" : "arXiv:1610.07922",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTHH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTHH_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTHH_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTWH" : {
        "cross_section" : 0.001582,
        "Source of cross section" : "arXiv:1610.07922",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTWH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTWH_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTWH_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    "TTWZ" : {
        "cross_section" : 0.003884,
        "Source of cross section" : "arXiv:1610.07922",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTWZ_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTWZ_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTWZ_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTZZ" : {
        "cross_section" : 0.001982,
        "Source of cross section" : "arXiv:1610.07922",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016:  'TTZZ_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTZZ_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTZZ_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTWW" : {
        "cross_section" : 0.01150,
        "Source of cross section" : "arXiv:1610.07922",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'TTWW_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTWW_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTWW_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # TTX
    "TTWJetsToLNu" : {
        "cross_section" : 0.1792,
        "Source of cross section" : "arXiv:1812.08622",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
            2017: 'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
            2018: 'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
        },
    },
    "TTZToLLNuNu": {
        "cross_section" : 0.2589,
        "Source of cross section" : "arXiv:1812.08622",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "ttHToNonbb" : {
        "cross_section" : 0.2151,
        "Source of cross section" : "",
        "Generator Info": "NLO PH+P8",
        "DAS": {
            2016: "ttHToNonbb_M125_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8",
            2017: 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
            2018: 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
        },
    },
    "ttHTobb" : {
        "cross_section" : 0.2151,
        "Source of cross section" : "",
        "Generator Info": "NLO PH+P8",
        "DAS": {
            2016: "ttHToNonbb_M125_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8",
            2017: 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
            2018: 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
        },
    },

    # VVV
    "WWW": {
        "cross_section" : 0.2086,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "ZZZ" : {
        "cross_section" : 0.01398,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "WZZ": {
        "cross_section" : 0.05565,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "WWZ" : {
        "cross_section" : 0.1651,
        "Source of cross section" : "MCM",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: "WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            2017: 'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WWZ_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },

    # VV
    "WZTo3LNu" : {
        "cross_section" : 4.4297,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: "WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            2017: "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8",
            2018: "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8",
        },
    },
    "WWTo2L2Nu" : {
        "cross_section" : 0.16975,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO PH+P8",
        "DAS": {
            2016: 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
            2017: 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
            2018: 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
        },
    },
    "VHTononbb" : {
        "cross_section" : 0.9561,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
            2017: 'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
            2018: 'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
        },
    },
    "ZZTo4L": {
        "cross_section" : 1.256,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO PH+P8",
        "DAS": {
            2016: "ZZ_TuneCUETP8M1_13TeV-pythia8",
            2017: "ZZTo4L_TuneCP5_13TeV-amcatnloFXFX-pythia8",
            2018: "ZZTo4L_TuneCP5_13TeV-amcatnloFXFX-pythia8",
        },
    },
    # "wpwpjj_ewk" : {
    #     "cross_section" : 0.03711,
    #     "Source of cross section" : "AN2018-062",
    #     "DAS": {
    #         2016: 'WpWpJJ_EWK-QCD_TuneCUETP8M1_13TeV-madgraph-pythia8',
    #         2017: 'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8',
    #         2018: 'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8',
    #     },
    # },

    # X+g
    "WWG" : {
        "cross_section" : 0.2147,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WWG_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WWG_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "WGToLNuG" : {
        "cross_section" : 405.271,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            2017: 'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8',
            2018: 'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8',
        },
    },
    "ZGToLLG" : {
        "cross_section" : 0.166,
        "Source of cross section" : "MCM",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'ZGTo2LG_PtG-130_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            2017: 'ZGTo2LG_PtG-130_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            2018: 'ZGTo2LG_PtG-130_TuneCP5_13TeV-amcatnloFXFX-pythia8',
        },
    },
    "WZG" : {
        "cross_section" : 0.04123,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "TGJets" : {
        "cross_section" : 2.967,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'TGJets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8',
            2017: 'TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8',
            2018: 'TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8',
        },
    },
    "TTGamma_Dilept" : {
        "cross_section" : 0.632,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: "TTGamma_Dilept_TuneCP5_PSweights_13TeV-madgraph-pythia8",
            2017: 'TTGamma_Dilept_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'TTGamma_Dilept_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTGamma_Hadronic" : {
        "cross_section" : 0.794,
        "Source of cross section" : "MCM",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: "TTGamma_Hadronic_TuneCP5_PSweights_13TeV-madgraph-pythia8",
            2017: 'TTGamma_Hadronic_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'TTGamma_Hadronic_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "TTGamma_SingleLept" : {
        "cross_section" : 5.048,
        "Source of cross section" : "MCM",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: "TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8",
            2017: 'TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'TTGamma_SingleLept_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # other
    "tZq" : {
        "cross_section" : 0.0736,
        "Source of cross section" : "MCM",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: "tZq_ll_4f_ckm_NLO_TuneCP5_PSweights_13TeV-amcatnlo-pythia8",
            2017: "tZq_ll_4f_ckm_NLO_TuneCP5_PSweights_13TeV-amcatnlo-pythia8",
            2018: "tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-madgraph-pythia8",
        },
    },
    "WJetsToLNu" : {
        "cross_section" : 61334.9,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: 'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            2017: 'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8',
            2018: 'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8',
        },
    },
    "TTJets": {
        "cross_section" : 831.762,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO MG+P8",
        "DAS": {
            2016: 'TTJets_TuneCUETP8M2T4_13TeV-amcatnloFXFX-pythia8',
            2017: 'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            2018: 'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
        },
    },
    'DYJetsToLL_M-10to50': {
        "cross_section" : 18610,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            2017: 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8',
            2018: 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8',
        },
    },
    'DYJetsToLL_M-50': {
        "cross_section" : 6020.85,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "LO MG+P8",
        "DAS": {
            2016: "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            2017: "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8",
            2018: "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8",
        },
    },
    "GluGluToH" : {
        "cross_section" : 0.01181,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO PH+P8",
        "DAS": {
            2016: "GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8",
            2017: 'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            2018: 'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
        },
    },
    "SingleTop" : {
        "cross_section" : 0.01123,
        "Source of cross section" : "AN2018-062",
        "Generator Info": "NLO PH+P8",
        "DAS": {
            2016: "ST_tWll_5f_LO_13TeV-MadGraph-pythia8",
            2017: 'ST_tWll_5f_LO_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'ST_tWll_5f_LO_TuneCP5_PSweights_13TeV-madgraph-pythia8',
        },
    },
    # "ttbar" : {
    #     "cross_section" : 689.7,
    #     "Source of cross section" : "MCM",
    #     "DAS": {
    #         2016: 'TT_TuneCUETP8M2T4_13TeV-powheg-pythia8',
    #         2017: 'TT_TuneCH3_13TeV-powheg-herwig7',
    #         2018: 'TT_TuneCH3_13TeV-powheg-herwig7',
    #     },
    # },
}
