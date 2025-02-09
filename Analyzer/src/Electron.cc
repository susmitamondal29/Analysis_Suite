#include "analysis_suite/Analyzer/interface/Electron.h"
#include "analysis_suite/Analyzer/interface/Jet.h"

void Electron::setup(TTreeReader& fReader, bool isMC)
{
    Lepton::setup("Electron", fReader, isMC);
    eCorr.setup(fReader, "Electron_eCorr");
    lostHits.setup(fReader, "Electron_lostHits");
    convVeto.setup(fReader, "Electron_convVeto");
    sieie.setup(fReader, "Electron_sieie");
    hoe.setup(fReader, "Electron_hoe");
    eInvMinusPInv.setup(fReader, "Electron_eInvMinusPInv");
    sip3d.setup(fReader, "Electron_sip3d");
    tightCharge.setup(fReader, "Electron_tightCharge");
    ecalSumEt.setup(fReader, "Electron_dr03EcalRecHitSumEt");
    hcalSumEt.setup(fReader, "Electron_dr03HcalDepth1TowerSumEt");
    tkSumPt.setup(fReader, "Electron_dr03TkSumPt");
    id = PID::Electron;
    mva_l.setup(fReader, "Electron_mvaFall17V2noIso_WPL");
    mva_80.setup(fReader, "Electron_mvaFall17V2noIso_WP80");
    mva_90.setup(fReader, "Electron_mvaFall17V2noIso_WP90");


    // 2017/2018 values
    ptRatioCut = 0.78;
    ptRelCut = 8.0;
    isoCut = 0.1;

    if(isMC) {
        auto corr_set = getScaleFile("EGM", "electron");
        electron_scale = WeightHolder(corr_set->at("UL-Electron-ID-SF"), Systematic::Electron_Scale,
                                      {"sf", "sfup", "sfdown"});
    }

}

void Electron::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 7
            && fabs(eta(i)) < 2.5
            // && convVeto.at(i)
            // && lostHits.at(i) <= 1
            && fabs(dz.at(i)) < 0.1
            && fabs(dxy.at(i)) < 0.05
            && mva_l.at(i)
            && iso.at(i) < 0.4
            // && fabs(eInvMinusPInv.at(i) < 0.01)
            // && hoe.at(i) < 0.08
            // && ((fabs(eta(i)) < BARREL_ETA && sieie.at(i) < 0.011) || (fabs(eta(i)) >= BARREL_ETA && sieie.at(i) < 0.031))
            )
            m_partList[Level::Loose]->push_back(i);
    }
}

/// closejet w iso
void Electron::createFakeList(Particle& jets)
{
    for (auto i : list(Level::Loose)) {
        if (mva_90.at(i)
            // sip3d.at(i) < 4
            // && lostHits.at(i) == 0
            && tightCharge.at(i) == 2
            ) {
            auto closejet_info = getCloseJet(i, jets);
            fakePtFactor[i] = fillFakePt(i, jets);
            if (getModPt(i) > 15) {
                m_partList[Level::Fake]->push_back(i);
                dynamic_cast<Jet&>(jets).closeJetDr_by_index.insert(closejet_info);
            }
        }
    }
}

// need iso
void Electron::createTightList(Particle& jets)
{
    for (auto i : list(Level::Fake)) {
        if (pt(i) > 15
            // && ecalSumEt.at(i) / pt(i) < 0.45
            // && hcalSumEt.at(i) / pt(i) < 0.25
            // && tkSumPt.at(i) / pt(i) < 0.2
            // && passMVACut(i, true)
            && passJetIsolation(i, jets))
            m_partList[Level::Tight]->push_back(i);
    }
}

float Electron::getScaleFactor()
{
    float weight = 1.;
    std::string syst = systName(electron_scale);
    for (auto eidx : list(Level::Tight)) {
        weight *= electron_scale.evaluate({yearMap.at(year_), syst, "wp90noiso", fabs(eta(eidx)), pt(eidx)});
    }
    return weight;
}
