#!/usr/bin/env python3

info = {
    "btag": {
        "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation",
        2016: {
            "Name": "DeepCSV_2016LegacySF_WP_V1.csv",
            "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy",
        },
        2017: {
            "Name": "DeepCSV_94XSF_WP_V4_B_F.csv",
            "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X",
        },

        2018: {
            "Name": "DeepCSV_102XSF_WP_V1.csv",
            "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X",
        },
    },
    "muonSF": {
        "URL": {
            "general":"https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOG",
            2016: "https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2016LegacyRereco",
            2017: "https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017",
            2018: "https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2018",
        },
        "Histogram": {
            2016: "NUM_MediumID_DEN_genTracks_eta_pt",
            2017: "NUM_MediumID_DEN_genTracks_pt_abseta",
            2018: "NUM_MediumID_DEN_TrackerMuons_pt_abseta",
        },
        "Name": ["MuonID_SF_{}.root", "MuonIso_SF_{}.root"]
    },
    
    "SUSYElectronSF": {
        "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSLeptonSF",
        "Name": "ElectronScaleFactors_Run{}.root",
        "TightList": ["Run{}_MVATightIP2D3DIDEmu",
                      "Run{}_ConvIHit0",
                      "Run{}_MultiIsoEmu"],
    },
    "RECOElectronSF": {
        2016: {
            "Name": ["egammaEffi.txt_EGM2D_updatedAll.root",
                     "egammaEffi.txt_EGM2D_updatedAll.root"],
            "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaIDRecipesRun2#80X_series_80X_Scale_factors_for",
        },
        2017: {
            "Name": ["egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root",
                     "egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root",],
            "URL": "https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Electron_Reconstruction_Scale_Fa",
        },
        2018: {
            "Name": ["EGM2D_BtoH_low_RecoSF_Legacy2016.root",
                     "EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root"],
            "URL": "https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#102X_series_Dataset_2018_Autumn",
        },
    },

    "pileup": {
        "URL": "https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData",
        "Exe": "ScaleFactors/pileup.py",
        "Name": "pileupSF.root",
    },

    "topTagger": {
        "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYHOTGroup",
        "Name": "TopTagSF_{}.root",
    },

    "btagEfficiency": {
        # No central place I got this
        "Name": "btageff__ttbar_powheg_pythia8_25ns_Moriond17_deepCSV.root",
        "Histogram" : ["h2_BTaggingEff_csv_med_Eff_b",
                       "h2_BTaggingEff_csv_med_Eff_c",
                       "h2_BTaggingEff_csv_med_Eff_udsg",]
    }
}
