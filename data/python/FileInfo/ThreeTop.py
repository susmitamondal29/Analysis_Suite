#!/usr/bin/env python3

info = {
    # TTT
    "tttj" : {
        "cross_section" : 0.0004741,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'TTTJ_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTTJ_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTTJ_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "tttw" : {
        "cross_section" : 0.000788,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'TTTW_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTTW_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTTW_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # TTTT
    "tttt" : {
        "cross_section" : 0.001197,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: 'TTTT_TuneCUETP8M2T4_13TeV-amcatnlo-pythia8',
            2017: 'TTTT_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'TTTT_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },

    # TTXY
    "ttzh" : {
        "cross_section" : 0.001535,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": {
            2016: 'TTZH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTZH_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTZH_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "tthh" : {
            "cross_section" : 0.000757,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": {
            2016: 'TTHH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTHH_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTHH_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "ttwh" : {
        "cross_section" : 0.001582,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": {
            2016: 'TTWH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTWH_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTWH_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    "ttwz" : {
        "cross_section" : 0.003884,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": {
            2016: 'TTWZ_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTWZ_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTWZ_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "ttzz" : {
        "cross_section" : 0.001982,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": {
            2016:  'TTZZ_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTZZ_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTZZ_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "ttww" : {
        "cross_section" : 0.01150,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": {
            2016: 'TTWW_TuneCUETP8M2T4_13TeV-madgraph-pythia8',
            2017: 'TTWW_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'TTWW_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # TTX
    "ttw" : {
        "cross_section" : 0.1792,
        "Source of cross section" : "arXiv:1812.08622",
        "DAS": {
            2016: 'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
            2017: 'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
            2018: 'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
        },
    },
    "ttz": {
        "cross_section" : 0.2589,
        "Source of cross section" : "arXiv:1812.08622",
        "DAS": {
            2016: 'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "ttz_m1-10": {
        "cross_section" : 0.0532,
        "Source of cross section" : "arXiv:1812.08622",
        "DAS": {
            2016: None,
            2017: 'TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "tth" : {
        "cross_section" : 0.2151,
        "Source of cross section" : "",
        "DAS": {
            2016: "ttHToNonbb_M125_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8",
            2017: 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
            2018: 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
        },
    },

    # VVV
    "www": {
        "cross_section" : 0.2086,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "zzz" : {
        "cross_section" : 0.01398,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "wzz": {
        "cross_section" : 0.05565,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "wwz" : {
        "cross_section" : 0.1651,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: "WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            2017: 'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WWZ_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },

    # VV
    "wzTo3lnu" : {
        "cross_section" : 4.4297,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            2017: "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8",
            2018: "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8",
        },
    },
    "ww_doubleScatter" : {
        "cross_section" : 0.16975,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
            2017: 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
            2018: 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
        },
    },
    "vh2nonbb" : {
        "cross_section" : 0.9561,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
            2017: 'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
            2018: 'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
        },
    },
    "zz4l": {
        "cross_section" : 1.256,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "ZZ_TuneCUETP8M1_13TeV-pythia8",
            2017: "ZZTo4L_TuneCP5_13TeV-amcatnloFXFX-pythia8",
            2018: "ZZTo4L_TuneCP5_13TeV-amcatnloFXFX-pythia8",
        },
    },
    "wpwpjj_ewk" : {
        "cross_section" : 0.03711,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WpWpJJ_EWK-QCD_TuneCUETP8M1_13TeV-madgraph-pythia8',
            2017: 'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8',
            2018: 'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # X+g
    "wwg" : {
        "cross_section" : 0.2147,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WWG_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WWG_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "wg" : {
          "cross_section" : 405.271,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            2017: 'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8',
            2018: 'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8',
        },
    },
    "zg" : {
        "cross_section" : 0.166,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: 'ZGTo2LG_PtG-130_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            2017: 'ZGTo2LG_PtG-130_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            2018: 'ZGTo2LG_PtG-130_TuneCP5_13TeV-amcatnloFXFX-pythia8',
        },
    },
    "wzg" : {
        "cross_section" : 0.04123,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            2017: 'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            2018: 'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
        },
    },
    "tg" : {
        "cross_section" : 2.967,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'TGJets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8',
            2017: 'TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8',
            2018: 'TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8',
        },
    },
    "ttg_dilep" : {
        "cross_section" : 0.632,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "TTGamma_Dilept_TuneCP5_PSweights_13TeV-madgraph-pythia8",
            2017: 'TTGamma_Dilept_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'TTGamma_Dilept_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "ttg_hadronic" : {
        "cross_section" : 0.794,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: "TTGamma_Hadronic_TuneCP5_PSweights_13TeV-madgraph-pythia8",
            2017: 'TTGamma_Hadronic_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'TTGamma_Hadronic_TuneCP5_13TeV-madgraph-pythia8',
        },
    },
    "ttg_singleLept" : {
        "cross_section" : 5.048,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: "TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8",
            2017: 'TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'TTGamma_SingleLept_TuneCP5_13TeV-madgraph-pythia8',
        },
    },

    # other
    "tzq" : {
        "cross_section" : 0.0736,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: "tZq_ll_4f_ckm_NLO_TuneCP5_PSweights_13TeV-amcatnlo-pythia8",
            2017: "tZq_ll_4f_ckm_NLO_TuneCP5_PSweights_13TeV-amcatnlo-pythia8",
            2018: "tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-madgraph-pythia8",
        },
    },
    "wjets" : {
        "cross_section" : 61334.9,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            2017: 'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8',
            2018: 'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8',
        },
    },
    "ttjet": {
        "cross_section" : 831.762,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: 'TTJets_TuneCUETP8M2T4_13TeV-amcatnloFXFX-pythia8',
            2017: 'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            2018: 'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
        },
    },
    'DYm10-50': {
        "cross_section" : 18610,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            2017: 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8',
            2018: 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8',
        },
    },
    'DYm50': {
        "cross_section" : 6020.85,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            2017: "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8",
            2018: "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8",
        },
    },
    "ggh2zz" : {
        "cross_section" : 0.01181,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8",
            2017: 'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            2018: 'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
        },
    },
    "st_twll" : {
        "cross_section" : 0.01123,
        "Source of cross section" : "AN2018-062",
        "DAS": {
            2016: "ST_tWll_5f_LO_13TeV-MadGraph-pythia8",
            2017: 'ST_tWll_5f_LO_TuneCP5_PSweights_13TeV-madgraph-pythia8',
            2018: 'ST_tWll_5f_LO_TuneCP5_PSweights_13TeV-madgraph-pythia8',
        },
    },
    "ttbar" : {
        "cross_section" : 689.7,
        "Source of cross section" : "MCM",
        "DAS": {
            2016: 'TT_TuneCUETP8M2T4_13TeV-powheg-pythia8',
            2017: 'TT_TuneCH3_13TeV-powheg-herwig7',
            2018: 'TT_TuneCH3_13TeV-powheg-herwig7',
        },
    },
}
