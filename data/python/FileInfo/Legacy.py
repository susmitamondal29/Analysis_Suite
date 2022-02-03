#!/usr/bin/env python3

info = {
    # TTT
    "tttj" : {
        "cross_section" : 0.0004741,
        "Source of cross section" : "AN2018-062",
        "DAS": 'TTTJ_Tune.*',
    },
    "tttw" : {
        "cross_section" : 0.000788,
        "Source of cross section" : "AN2018-062",
        "DAS": 'TTTW_Tune.*',
    },

    # TTTT
    "tttt" : {
        "cross_section" : 0.001197,
        "Source of cross section" : "MCM",
        "DAS": 'TTTT_Tune.*',
    },

    # TTXY
    "ttzh" : {
        "cross_section" : 0.001535,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": 'TTZH_Tune.*',
    },
    "tthh" : {
            "cross_section" : 0.000757,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": 'TTHH_Tune.*',
    },
    "ttwh" : {
        "cross_section" : 0.001582,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": 'TTWH_Tune.*',
    },

    "ttwz" : {
        "cross_section" : 0.003884,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": 'TTWZ_Tune.*',
    },
    "ttzz" : {
        "cross_section" : 0.001982,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": 'TTZZ_Tune.*',
    },
    "ttww" : {
        "cross_section" : 0.01150,
        "Source of cross section" : "arXiv:1610.07922",
        "DAS": 'TTWW_Tune.*',
    },

    # TTX
    "ttw" : {
        "cross_section" : 0.1792,
        "Source of cross section" : "arXiv:1812.08622",
        "DAS": 'TTWJetsToLNu_Tune.*'
    },
    "ttz": {
        "cross_section" : 0.2589,
        "Source of cross section" : "arXiv:1812.08622",
        "DAS": 'TTZToLLNuNu_M-10_Tune.*',
    },
    "ttz_m1-10": {
        "cross_section" : 0.0532,
        "Source of cross section" : "arXiv:1812.08622",
        "DAS": "TTZToLL_M-1to10_Tune.*",
    },
    "tth" : {
        "cross_section" : 0.2151,
        "Source of cross section" : "",
        "DAS" : "ttHToNonbb_M125_Tune.*",
    },

    # VVV
    "www": {
        "cross_section" : 0.2086,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WWW_4F_Tune.*',
    },
    "zzz" : {
        "cross_section" : 0.01398,
        "Source of cross section" : "AN2018-062",
        "DAS": 'ZZZ_Tune.*',
    },
    "wzz": {
        "cross_section" : 0.05565,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WZZ_Tune.*'
    },
    "wwz" : {
        "cross_section" : 0.1651,
        "Source of cross section" : "MCM",
        "DAS": 'WWZ_.*Tune.*',
    },

    # VV
    "wzTo3lnu" : {
        "cross_section" : 4.4297,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WZTo3LNu_Tune.*',
    },
    "ww_doubleScatter" : {
        "cross_section" : 0.16975,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WWTo2L2Nu_DoubleScattering_.*',
    },
    "vh2nonbb" : {
        "cross_section" : 0.9561,
        "Source of cross section" : "AN2018-062",
        "DAS": 'VHToNonbb_M125_13TeV.*',
    },
    "zz4l": {
        "cross_section" : 1.256,
        "Source of cross section" : "AN2018-062",
        "DAS": 'ZZ.*_Tune',
    },
    "wpwpjj_ewk" : {
        "cross_section" : 0.03711,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WpWpJJ_EWK-QCD_Tune.*',
    },

    # X+g
    "wwg" : {
        "cross_section" : 0.2147,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WWG_Tune.*',
    },
    "wg" : {
          "cross_section" : 405.271,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WGToLNuG_Tune.*',
    },
    "zg" : {
        "cross_section" : 0.166,
        "Source of cross section" : "MCM",
        "DAS": 'ZGTo2LG_PtG-130_Tune.*',
    },
    "wzg" : {
        "cross_section" : 0.04123,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WZG_Tune.*',
    },
    "tg" : {
        "cross_section" : 2.967,
        "Source of cross section" : "AN2018-062",
        "DAS": 'TGJets_Tune.*',
    },
    "ttg_dilep" : {
        "cross_section" : 0.632,
        "Source of cross section" : "AN2018-062",
        "DAS": 'TTGamma_Dilept_Tune.*',
    },
    "ttg_hadronic" : {
        "cross_section" : 0.794,
        "Source of cross section" : "MCM",
        "DAS": 'TTGamma_Hadronic_Tune.*',
    },
    "ttg_singleLept" : {
        "cross_section" : 5.048,
        "Source of cross section" : "MCM",
        "DAS": 'TTGamma_SingleLept_Tune.*',
    },

    # other
    "tzq" : {
        "cross_section" : 0.0736,
        "Source of cross section" : "MCM",
        "DAS": 'tZq_ll_4f_ckm_NLO_Tune.*',
    },
    "wjets" : {
        "cross_section" : 61334.9,
        "Source of cross section" : "AN2018-062",
        "DAS": 'WJetsToLNu_Tune.*',
    },
    "ttjet": {
        "cross_section" : 831.762,
        "Source of cross section" : "AN2018-062",
        "DAS": 'TTJets_Tune.*',
    },
    'DYm10-50': {
        "cross_section" : 18610,
        "Source of cross section" : "AN2018-062",
        "DAS": 'DYJetsToLL_M-10to50_Tune.*',
    },
    'DYm50': {
        "cross_section" : 6020.85,
        "Source of cross section" : "AN2018-062",
        "DAS": 'DYJetsToLL_M-50_Tune.*',
    },
    "ggh2zz" : {
        "cross_section" : 0.01181,
        "Source of cross section" : "AN2018-062",
        "DAS": 'GluGluHToZZTo4L_M125_13TeV.*',
    },
    "st_twll" : {
        "cross_section" : 0.01123,
        "Source of cross section" : "AN2018-062",
        "DAS": 'ST_tWll_5f_LO_.*',
    },
    "ttbar" : {
        "cross_section" : 689.7,
        "Source of cross section" : "MCM",
        "DAS": 'TT_Tune.*',
    },

    "data" : {
        "cross_section" : 1,
        "DAS": "dummy",
    },
    #
    "qcd_mu_pt15-20" : {
        "cross_section" : 3678000,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-15to20_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt20-30" : {
        "cross_section" : 3189000,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-20to30_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt30-50" : {
        "cross_section" : 1662000,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-30to50_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt50-80" : {
        "cross_section" : 452200,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-50to80_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt80-120" : {
        "cross_section" : 106500,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-80to120_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt120-170" : {
        "cross_section" : 25700,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-120to170_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt170-300" : {
        "cross_section" : 8683,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-170to300_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt300-470" : {
        "cross_section" : 800.9,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-300to470_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt470-600" : {
        "cross_section" : 79.37,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-470to600_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt600-800" : {
        "cross_section" : 25.31,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-600to800_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt800-1000" : {
        "cross_section" : 4.723,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-800to1000_MuEnrichedPt5_Tune.*',
    },
    "qcd_mu_pt1000-Inf" : {
        "cross_section" : 1.62,
        "Source of cross section" : "XSDB",
        "DAS": 'QCD_Pt-1000toInf_MuEnrichedPt5_Tune.*',
    },
    # electron enriched
    "qcd_em_pt15-20" : {
        "cross_section" : 1327000,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-15to20_EMEnriched_Tune.*",
    },
    "qcd_em_pt20-30" : {
        "cross_section" : 4897000,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-20to30_EMEnriched_Tune.*",
    },
    "qcd_em_pt30-50" : {
        "cross_section" : 6379000,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-30to50_EMEnriched_Tune.*",
    },
    "qcd_em_pt50-80" : {
        "cross_section" : 1984000,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-50to80_EMEnriched_Tune.*",
    },
    "qcd_em_pt80-120" : {
        "cross_section" : 366500,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-80to120_EMEnriched_Tune.*",
    },
    "qcd_em_pt120-170" : {
        "cross_section" : 66490,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-120to170_EMEnriched_Tune.*",
    },
    "qcd_em_pt170-300" : {
        "cross_section" : 16480,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-170to300_EMEnriched_Tune.*",
    },
    "qcd_em_pt300-Inf" : {
        "cross_section" : 1097,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt-300toInf_EMEnriched_Tune.*",
    },
    # QCD bc
    "qcd_bcToE_pt15-20" : {
        "cross_section" : 186200,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt_15to20_bcToE_Tune.*",
    },
    "qcd_bcToE_pt20-30" : {
        "cross_section" : 303800,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt_20to30_bcToE_Tune.*",
    },
    "qcd_bcToE_pt30-80" : {
        "cross_section" : 362300,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt_30to80_bcToE_Tune.*",
    },
    "qcd_bcToE_pt80-170" : {
        "cross_section" : 33700,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt_80to170_bcToE_Tune.*",
    },
    "qcd_bcToE_pt170-250" : {
        "cross_section" : 2125,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt_170to250_bcToE_Tune.*",
    },
    "qcd_bcToE_pt250-Inf" : {
        "cross_section" : 562.5,
        "Source of cross section" : "XSDB",
        "DAS" : "QCD_Pt_250toInf_bcToE_Tune.*",
    },
}
