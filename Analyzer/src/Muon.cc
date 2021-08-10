#include "analysis_suite/Analyzer/interface/Muon.h"
#include "analysis_suite/Analyzer/interface/Jet.h"

void Muon::setup(TTreeReader& fReader)
{
    Lepton::setup("Muon", fReader);
    isGlobal = new TTRArray<Bool_t>(fReader, "Muon_isGlobal");
    isTracker = new TTRArray<Bool_t>(fReader, "Muon_isTracker");
    isPFcand = new TTRArray<Bool_t>(fReader, "Muon_isPFcand");
    iso = new TTRArray<Float_t>(fReader, "Muon_miniPFRelIso_all");
    dz = new TTRArray<Float_t>(fReader, "Muon_dz");
    dxy = new TTRArray<Float_t>(fReader, "Muon_dxy");
    tightCharge = new TTRArray<Int_t>(fReader, "Muon_tightCharge");
    mediumId = new TTRArray<Bool_t>(fReader, "Muon_mediumId");
    sip3d = new TTRArray<Float_t>(fReader, "Muon_sip3d");

    if (year_ == Year::yr2016) {
        ptRatioCut = 0.76;
        ptRelCut = pow(7.2, 2);
    } else {
        ptRatioCut = 0.74;
        ptRelCut = pow(6.8, 2);
    }

    setSF<TH2D>("muonSF", Systematic::Muon_ID);
}

void Muon::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 5
            && fabs(eta(i)) < 2.4
            && (isGlobal->At(i) || isTracker->At(i))
            && isPFcand->At(i)
            && iso->At(i) < 0.4
            && fabs(dz->At(i)) < 0.1
            && fabs(dxy->At(i)) < 0.05)
            m_partList[Level::Loose]->push_back(i);
    }
}

void Muon::createFakeList(Particle& jets)
{
    for (auto i : list(Level::Loose)) {
        if (pt(i) > 10
            && tightCharge->At(i) == 2
            && mediumId->At(i) && sip3d->At(i) < 4) {
            m_partList[Level::Fake]->push_back(i);
            dynamic_cast<Jet&>(jets).closeJetDr_by_index.insert(getCloseJet(i, jets));
        }
    }
}

void Muon::createTightList(Particle& jets)
{
    for (auto i : list(Level::Fake)) {
        if (pt(i) > 15
            && iso->At(i) < 0.16
            && passJetIsolation(i, jets))
            m_partList[Level::Tight]->push_back(i);
    }
}

float Muon::getScaleFactor()
{
    float weight = 1.;
    for (auto midx : list(Level::Tight)) {
        float fixed_pt = std::max(std::min(pt(midx), ptMax), ptMin);
        if (year_ == Year::yr2016) {
            weight *= getWeight("muonSF", eta(midx), fixed_pt);
        } else {
            weight *= getWeight("muonSF", fixed_pt, fabs(eta(midx)));
        }
    }
    return weight;
}
