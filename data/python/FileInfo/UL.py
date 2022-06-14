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
    "tth_bb" : {
        "cross_section" : 0.2151,
        "Source of cross section" : "",
        "DAS" : "ttHTobb_M125_Tune.*",
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
        "DAS": 'WWZ_4F_Tune.*',
    },

    # # VV
    # "wzTo3lnu" : {
    #     "cross_section" : 4.4297,
    #     "Source of cross section" : "AN2018-062",
    #     "DAS": 'WZTo3LNu_Tune.*',
    # },
    # "ww_doubleScatter" : {
    #     "cross_section" : 0.16975,
    #     "Source of cross section" : "AN2018-062",
    #     "DAS": 'WWTo2L2Nu_DoubleScattering_.*',
    # },
    # "vh2nonbb" : {
    #     "cross_section" : 0.9561,
    #     "Source of cross section" : "AN2018-062",
    #     "DAS": 'VHToNonbb_M125_13TeV.*',
    # },
    # "zz4l": {
    #     # "cross_section" : 1.256,
    #     "cross_section": 16.523,
    #     "Source of cross section" : "AN2018-062",
    #     "DAS": 'ZZ.*_Tune',
    # },
    # "wpwpjj_ewk" : {
    #     "cross_section" : 0.03711,
    #     "Source of cross section" : "AN2018-062",
    #     "DAS": 'WpWpJJ_EWK-QCD_Tune.*',
    # },

    ## VV Inclusive
    "zz" : {
        "cross_section": 16.523,
        "Level": "NLO",
        "Source of cross section": "1G25ns",
        "DAS": "ZZ_TuneC.*",
    },
    "wz" : {
        "cross_section": 47.13,
        "Level": "NLO",
        "Source of cross section": "1G25ns",
        "DAS": "WZ_TuneC.*",
    },
    "ww" : {
        "cross_section": 113.898,
        "Level": "NLO",
        "Source of cross section": "1G25ns",
        "DAS": "WW_Tune.*",
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
        "DAS": 'ZGToLLG_01J_5f_Tune.*',
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
    "ggh2zz" : {
        "cross_section" : 0.01181,
        "Source of cross section" : "AN2018-062",
        "DAS": 'GluGluHToZZTo4L_M125_Tune.*',
    },
    "st_twll" : {
        "cross_section" : 0.01123,
        "Source of cross section" : "AN2018-062",
        "DAS": 'ST_tW_Dilept_5f.*',
    },

    "data" : {
        "cross_section" : 1,
        "DAS": "dummy",
    },

    # TTBar samples
    "ttbar" : {
        "cross_section" : 831.762,
        "Source of cross section" : "MCM",
        "DAS": 'TT_Tune.*',
    },
    "ttbar_2l2n": {
        "cross_section" : 88.29,
        "DAS" : "TTTo2L2Nu_Tune.*",
    },
    "ttbar_semilep": {
        "cross_section" : 365.34,
        "DAS" : "TTToSemiLeptonic_Tune.*",
    },
    "ttbar_hadronic": {
        "cross_section" : 377.96,
        "DAS" : "TTToHadronic_Tune.*",
    },

    # Drell-Yan
    'DYm10-50': {
        "cross_section" : 18610.0,
        "Source of cross section" : "1G25ns",
        "Level": "NLO",
        "DAS": 'DYJetsToLL_M-10to50_Tune.*',
    },
    'DYm50': {
        "cross_section" : 6077.22,
        "Source of cross section" : "1G25ns",
        "Level": "NNLO",
        "DAS": 'DYJetsToLL_M-50_Tune.*madgraphMLM-pythia8',
    },
    'DYm50_amc': {
        "cross_section" : 6404.,
        "Source of cross section" : "1G25ns",
        "Level": "NNLO",
        "DAS": 'DYJetsToLL_M-50_Tune.*amcatnloFXFX-pythia8',
    },
    "DYm50_ht40-70" : {
        "cross_section": 311.4,
        "DAS" : "DYJetsToLL_M-50_HT-40to70_Tune.*",
    },
    "DYm50_ht70-100" : {
        "cross_section": 145.5,
        "DAS" : "DYJetsToLL_M-50_HT-70to100_Tune.*",
    },
    "DYm50_ht100-200" : {
        "cross_section": 160.7,
        "DAS" : "DYJetsToLL_M-50_HT-100to200_Tune.*",
    },
    "DYm50_ht200-400" : {
        "cross_section": 48.63,
        "DAS" : "DYJetsToLL_M-50_HT-200to400_Tune.*",
    },
    "DYm50_ht400-600" : {
        "cross_section": 6.993,
        "DAS" : "DYJetsToLL_M-50_HT-400to600_Tune.*",
    },
    "DYm50_ht600-800" : {
        "cross_section": 1.761,
        "DAS" : "DYJetsToLL_M-50_HT-600to800_Tune.*",
    },
    "DYm50_ht800-1200" : {
        "cross_section": 0.8021,
        "DAS" : "DYJetsToLL_M-50_HT-800to1200_Tune.*",
    },
    "DYm50_ht1200-2500" : {
        "cross_section": 0.1937,
        "DAS" : "DYJetsToLL_M-50_HT-1200to2500_Tune.*",
    },
    "DYm50_ht2500-Inf" : {
        "cross_section": 0.003514,
        "DAS" : "DYJetsToLL_M-50_HT-2500toInf_Tune.*",
    },

    # W + Jets
    "wjets_ht70-100" : {
        "cross_section": 1292.0,
        "DAS" : "WJetsToLNu_HT-70To100_TuneC*",
    },
    "wjets_ht100-200": {
        "cross_section": 1256.0,
        "DAS" : "WJetsToLNu_HT-100To200_TuneC*",
    },
    "wjets_ht200-400": {
        "cross_section": 407.9,
        "DAS" : "WJetsToLNu_HT-200To400_TuneC*",
    },
    "wjets_ht400-600": {
        "cross_section": 57.48,
        "DAS" : "WJetsToLNu_HT-400To600_TuneC*",
    },
    "wjets_ht600-800": {
        "cross_section": 12.87,
        "DAS" : "WJetsToLNu_HT-600To800_TuneC*",
    },
    "wjets_ht800-1200": {
        "cross_section": 5.366,
        "DAS" : "WJetsToLNu_HT-800To1200_TuneC*",
    },
    "wjets_ht1200-2500": {
        "cross_section": 1.15,
        "DAS" : "WJetsToLNu_HT-1200To2500_TuneC*",
    },
    "wjets_ht2500-Inf": {
        "cross_section": 0.008001,
        "DAS" :   "WJetsToLNu_HT-2500ToInf_TuneC*",
    },

    # "qcd_mu15_pt20-Inf" : {
    #     "cross_section" : { "2016": 269900, "2017/2018": 239400, },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-20toInf_MuEnrichedPt15_Tune.*',
    # },
    # "qcd_mu_pt15-20" : {
    #     "cross_section" : { "2016": 3678000, "2017/2018": 2797000 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-15to20_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt20-30" : {
    #     "cross_section" : { "2016": 3189000, "2017/2018": 2526000 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-20to30_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt30-50" : {
    #     "cross_section" : { "2016": 1662000, "2017/2018": 1362000 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-30to50_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt50-80" : {
    #     "cross_section" : { "2016": 452200, "2017/2018": 376600 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-50to80_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt80-120" : {
    #     "cross_section" : { "2016": 106500, "2017/2018": 88930 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-80to120_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt120-170" : {
    #     "cross_section" : { "2016": 25700, "2017/2018": 21230 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-120to170_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt170-300" : {
    #     "cross_section" : { "2016": 8683, "2017/2018": 7055 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-170to300_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt300-470" : {
    #     "cross_section" : { "2016": 800.9, "2017/2018": 797.3 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-300to470_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt470-600" : {
    #     "cross_section" : { "2016": 79.37, "2017/2018": 59.24 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-470to600_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt600-800" : {
    #     "cross_section" : { "2016": 25.31, "2017/2018": 18.22 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-600to800_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt800-1000" : {
    #     "cross_section" : { "2016": 4.723, "2017/2018": 3.275 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-800to1000_MuEnrichedPt5_Tune.*',
    # },
    # "qcd_mu_pt1000-Inf" : {
    #     "cross_section" : { "2016": 1.62, "2017/2018": 1.078 },
    #     "Source of cross section" : "XSDB",
    #     "DAS": 'QCD_Pt-1000toInf_MuEnrichedPt5_Tune.*',
    # },

    # # electron enriched
    # "qcd_em_pt15-20" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-15to20_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt20-30" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-20to30_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt30-50" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-30to50_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt50-80" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-50to80_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt80-120" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-80to120_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt120-170" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-120to170_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt170-300" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-170to300_EMEnriched_Tune.*",
    # },
    # "qcd_em_pt300-Inf" : {
    #     "cross_section" : ,
    #     "Level": "LO",
    #     "Source of cross section" : "XSDB",
    #     "DAS" : "QCD_Pt-300toInf_EMEnriched_Tune.*",
    # },
    # QCD bc
    "qcd_bcToE_pt15-20" : {
        "cross_section" :  1272980000,
        'kfactor': 0.0002,
        "Level": "LO",
        "Source of cross section" : "1G25ns",
        "DAS" : "QCD_Pt_15to20_bcToE_Tune.*",
    },
    "qcd_bcToE_pt20-30" : {
        "cross_section" : 557627000,
        'kfactor': 0.00059 ,
        "Level": "LO",
        "Source of cross section" : "1G25ns",
        "DAS" : "QCD_Pt_20to30_bcToE_Tune.*",
    },
    "qcd_bcToE_pt30-80" : {
        "cross_section" : 159068000,
        'kfactor': 0.00255,
        "Level": "LO",
        "Source of cross section" : "1G25ns",
        "DAS" : "QCD_Pt_30to80_bcToE_Tune.*",
    },
    "qcd_bcToE_pt80-170" : {
        "cross_section" : 3221000,
        'kfactor': 0.01183,
        "Level": "LO",
        "Source of cross section" : "1G25ns",
        "DAS" : "QCD_Pt_80to170_bcToE_Tune.*",
    },
    "qcd_bcToE_pt170-250" : {
        "cross_section" : 105771,
        'kfactor': 0.02492,
        "Level": "LO",
        "Source of cross section" : "1G25ns",
        "DAS" : "QCD_Pt_170to250_bcToE_Tune.*",
    },
    "qcd_bcToE_pt250-Inf" : {
        "cross_section" : 21094.1,
        'kfactor': 0.03375,
        "Level": "LO",
        "Source of cross section" : "1G25ns",
        "DAS" : "QCD_Pt_250toInf_bcToE_Tune.*",
    },
}
