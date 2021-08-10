#!/usr/bin/env python3

info = {
    "Muon_ID": {
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
        "File": "MuonID_SF_{}.root",
    },
    "Muon_Iso": {
        "Histogram": {
            2016: "NUM_TightRelIso_DEN_MediumID_eta_pt",
            2017: "NUM_TightRelIso_DEN_MediumID_pt_abseta",
            2018: "NUM_TightRelIso_DEN_MediumID_pt_abseta",
        },
        "File": "MuonIso_SF_{}.root",
    },
    "ElectronSF_low": {
        "Histogram": "EGamma_SF2D",
        "File": {
            2016: "egammaEffi.txt_EGM2D_updatedAll.root",
            2017: "egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root",
            2018: "EGM2D_BtoH_low_RecoSF_Legacy2016.root",
        },
    },
    "ElectronSF": {
        "URL": [
            "https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaIDRecipesRun2#80X_series_80X_Scale_factors_for",
            "https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Electron_Reconstruction_Scale_Fa",
            "https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#102X_series_Dataset_2018_Autumn",
        ],
        "Histogram": "EGamma_SF2D",
        "File": {
            2016: "egammaEffi.txt_EGM2D_updatedAll.root",
            2017: "egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root",
            2018: "EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root",
        },
    },
    "Electron_Susy": {
        "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSLeptonSF",
        "Histogram": [
            ("Run{}_MVATightIP2D3DIDEmu", "Electron_MVATightIP2D3DIDEmu"),
            ("Run{}_ConvIHit0", "Electron_ConvIHit0"),
            ("Run{}_MultiIsoEmu", "Electron_MultiIsoEmu"),
        ],
        "File": "ElectronScaleFactors_Run{}.root",
    },
    "BJet_Eff": {
        # No central place I got this
        "File": "btageff__ttbar_powheg_pythia8_25ns_Moriond17_deepCSV.root",
        "Histogram" : [
            ("h2_BTaggingEff_csv_med_Eff_b", "btagEff_b"),
            ("h2_BTaggingEff_csv_med_Eff_c", "btagEff_c"),
            ("h2_BTaggingEff_csv_med_Eff_udsg", "btagEff_udsg"),
        ],
    },
    "topTagger": {
        "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYHOTGroup",
        "Histogram": [
            ("{}/hSF_SIG", "topSF_{}_True"),
            ("{}/hSF_BG", "topSF_{}_Fake"),
        ],
        "File": [
            ("TopTagSF_LWP.root", "LWP"),
            ("TopTagSF_MWP.root", "MWP"),
            ("TopTagSF_TWP.root", "TWP"),
            ("TopTagSF_AltTWP.root", "AltTWP"),
        ],
    },
    "pileup": {
        "URL": "https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData",
        "Histogram": [
            ("pileupSF_{}_nom", "pileupSF"),
            ("pileupSF_{}_up", "pileupSF_up"),
            ("pileupSF_{}_dn", "pileupSF_down"),
        ],
        "File": "pileupSF.root",
    },


    # "btag": {
    #     "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation",
    #     2016: {
    #         "Name": "DeepCSV_2016LegacySF_WP_V1.csv",
    #         "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy",
    #     },
    #     2017: {
    #         "Name": "DeepCSV_94XSF_WP_V4_B_F.csv",
    #         "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X",
    #     },

    #     2018: {
    #         "Name": "DeepCSV_102XSF_WP_V1.csv",
    #         "URL": "https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X",
    #     },
    # },

}
