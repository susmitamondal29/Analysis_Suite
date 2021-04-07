#include "analysis_suite/Analyzer/interface/ScaleFactors.h"

#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include <filesystem>

ScaleFactors::ScaleFactors(int year)
    : year_(year)
{
    std::string scaleDir = getenv("CMSSW_BASE");
    scaleDir += "/src/analysis_suite/data/scale_factors/";

    std::string strYear;
    if (year == yr2016) {
        calib = BTagCalibration("deepcsv", scaleDir + "btag_2016.csv");
        strYear = "2016";
    } else if (year == yr2017) {
        calib = BTagCalibration("deepcsv", scaleDir + "btag_2017.csv");
        strYear = "2017";
    } else {
        calib = BTagCalibration("deepcsv", scaleDir + "btag_2018.csv");
        strYear = "2018";
    }
    btag_reader = BTagCalibrationReader(BTagEntry::OP_MEDIUM, "central");
    btag_reader.load(calib, BTagEntry::FLAV_B, "comb");
    btag_reader.load(calib, BTagEntry::FLAV_C, "comb");
    btag_reader.load(calib, BTagEntry::FLAV_UDSG, "incl");

    std::cout << scaleDir + "event_scalefactors.root" << std::endl;
    TFile* f_scale_factors = new TFile((scaleDir + "event_scalefactors.root").c_str());
    f_scale_factors->cd(strYear.c_str());
    pileupSF = (TH1D*)gDirectory->Get("pileupSF");
    topSF = (TH1F*)gDirectory->Get("topSF_TWP_True");
    fakeTopSF = (TH1F*)gDirectory->Get("topSF_MWP_Fake");
    electronLowSF = (TH2F*)gDirectory->Get("electronSF_low");
    electronSF = (TH2F*)gDirectory->Get("electronSF");
    electronSusySF = (TH2F*)gDirectory->Get("electronSF_susy");
    muonSF = (TH2D*)gDirectory->Get("muonSF");
    h_btag_eff_b = (TH2D*)gDirectory->Get("btagEff_b");
    h_btag_eff_c = (TH2D*)gDirectory->Get("btagEff_c");
    h_btag_eff_udsg = (TH2D*)gDirectory->Get("btagEff_udsg");
}

float ScaleFactors::getBJetSF(Jet& jets)
{

    float weight = 1.;
    auto goodBJets = jets.bjetList;
    BTagEntry::JetFlavor flav;

    for (auto bidx : goodBJets) {
        int pdgId = std::abs(jets.hadronFlavour->At(bidx));
        if (pdgId == PID_BJET)
            flav = BTagEntry::FLAV_B;
        else if (pdgId == PID_CJET)
            flav = BTagEntry::FLAV_C;
        else
            flav = BTagEntry::FLAV_UDSG;
        weight *= btag_reader.eval_auto_bounds("central", flav, jets.eta->At(bidx), jets.pt->At(bidx));
    }
    for (auto jidx : jets.tightList) {
        if (std::find(goodBJets.begin(), goodBJets.end(), jidx) != goodBJets.end()) {
            continue; // is a bjet, weighting already taken care of
        }
        int pdgId = std::abs(jets.hadronFlavour->At(jidx));
        float pt = jets.pt->At(jidx);
        float eta = fabs(jets.eta->At(jidx));
        float eff = 1;
        if (pdgId == PID_BJET) {
            flav = BTagEntry::FLAV_B;
            eff = getWeight(h_btag_eff_b, pt, eta);
        } else if (pdgId == PID_CJET) {
            flav = BTagEntry::FLAV_C;
            eff = getWeight(h_btag_eff_c, pt, eta);
        } else {
            flav = BTagEntry::FLAV_UDSG;
            eff = getWeight(h_btag_eff_udsg, pt, eta);
        }
        double bSF = btag_reader.eval_auto_bounds("central", flav, jets.eta->At(jidx), jets.pt->At(jidx));
        weight *= (1 - bSF * eff) / (1 - eff);
    }

    return weight;
}

float ScaleFactors::getPileupSF(int nPU)
{
    return getWeight(pileupSF, nPU);
}

float ScaleFactors::getResolvedTopSF(ResolvedTop& top, GenParticle& genPart)
{
    float weight = 1.;
    for (auto tidx : top.looseList) {
        bool foundMatch = false;
        float minDR = 0.1;
        float tpt = top.pt->At(tidx);
        float teta = top.eta->At(tidx);
        float tphi = top.phi->At(tidx);
        for (auto gidx : genPart.topList) {
            float dr2 = pow(genPart.eta->At(gidx) - teta, 2)
                + pow(genPart.phi->At(gidx) - tphi, 2);
            if (dr2 < minDR) {
                foundMatch = true;
                weight *= getWeight(topSF, tpt);
                break;
            }
        }
        if (!foundMatch) {
            weight *= getWeight(fakeTopSF, tpt);
        }
    }
    return weight;
}

float ScaleFactors::getElectronSF(Lepton& electron)
{
    float weight = 1.;
    for (auto eidx : electron.tightList) {
        float pt = std::min(electron.pt->At(eidx), elecPtMax);
        float eta = electron.eta->At(eidx);
        if (pt < 20) {
            weight *= getWeight(electronLowSF, eta, pt);
        } else {
            weight *= getWeight(electronSF, eta, pt);
        }
        weight *= getWeight(electronSusySF, eta, pt);
    }
    return weight;
}

float ScaleFactors::getMuonSF(Lepton& muon)
{
    float weight = 1.;
    for (auto midx : muon.tightList) {
        float pt = std::min(muon.pt->At(midx), muonPtMax);
        if (pt < muonPtMin)
            pt = muonPtMin;
        float eta = muon.eta->At(midx);
        weight *= (year_ == yr2016) ? getWeight(muonSF, eta, pt) : getWeightPtAbsEta(muonSF, pt, eta);
    }

    return weight;
}
