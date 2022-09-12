#include "analysis_suite/Analyzer/interface/Muon.h"
#include "analysis_suite/Analyzer/interface/Jet.h"

void Muon::setup(TTreeReader& fReader, bool isMC)
{
    Lepton::setup("Muon", fReader, isMC);
    isGlobal.setup(fReader, "Muon_isGlobal");
    isTracker.setup(fReader, "Muon_isTracker");
    isPFcand.setup(fReader, "Muon_isPFcand");
    tightCharge.setup(fReader, "Muon_tightCharge");
    mediumId.setup(fReader, "Muon_mediumId");

    id = PID::Muon;

    if (isMC) {
        auto corr_set = getScaleFile("MUO", "muon_Z");
        muon_scale = WeightHolder(corr_set->at("NUM_MediumID_DEN_TrackerMuons"), Systematic::Muon_Scale,
                                  {"sf", "systup", "systdown"});
    }
    cone_correction = 0.85;
    // mvaCut = 0.65;
    // isoCut = 0.16;
    // ptRatioCut = 0.76;
    // ptRelCut = 7.2;

}

void Muon::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 5
            && fabs(eta(i)) < 2.4
            && (isGlobal.at(i) || isTracker.at(i))
            && isPFcand.at(i)
            && iso.at(i) < 0.4
            && fabs(dz.at(i)) < 0.1
            && fabs(dxy.at(i)) < 0.05)
            m_partList[Level::Loose]->push_back(i);
    }
}

void Muon::createFakeList(Particle& jets)
{
    for (auto i : list(Level::Loose)) {
        if (tightCharge.at(i) == 2
            && mediumId.at(i)
            && sip3d.at(i) < 4
            && m_pt.at(i)*getFakePtFactor(i) > 15
            && ptRatio(i) > 0.4)
            {
                m_partList[Level::Fake]->push_back(i);
                dynamic_cast<Jet&>(jets).closeJetDr_by_index.insert(getCloseJet(i, jets));
            }
    }
}

void Muon::createTightList(Particle& jets)
{
    for (auto i : list(Level::Fake)) {
        if (pt(i) > 15
            && passJetIsolation(i)
            ) {
            m_partList[Level::Tight]->push_back(i);
        } else {
            fakePtFactor[i] = getFakePtFactor(i);
        }

    } 
}

float Muon::getScaleFactor()
{
    float weight = 1.;
    std::string syst = systName(muon_scale);
    for (auto midx : list(Level::Tight)) {
        weight *= muon_scale.evaluate({yearMap.at(year_)+"_UL", fabs(eta(midx)), pt(midx), syst});
    }
    return weight;
}
