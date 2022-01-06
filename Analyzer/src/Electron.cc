#include "analysis_suite/Analyzer/interface/Electron.h"
#include "analysis_suite/Analyzer/interface/Jet.h"

void Electron::setup(TTreeReader& fReader, bool isMC)
{
    Lepton::setup("Electron", fReader, isMC);
    eCorr.setup(fReader, "Electron_eCorr");
    lostHits.setup(fReader, "Electron_lostHits");
    convVeto.setup(fReader, "Electron_convVeto");
    iso.setup(fReader, "Electron_miniPFRelIso_all");
    sieie.setup(fReader, "Electron_sieie");
    hoe.setup(fReader, "Electron_hoe");
    eInvMinusPInv.setup(fReader, "Electron_eInvMinusPInv");
    sip3d.setup(fReader, "Electron_sip3d");
    tightCharge.setup(fReader, "Electron_tightCharge");
    ecalSumEt.setup(fReader, "Electron_dr03EcalRecHitSumEt");
    hcalSumEt.setup(fReader, "Electron_dr03HcalDepth1TowerSumEt");
    tkSumPt.setup(fReader, "Electron_dr03TkSumPt");

    ptRatioCut = 0.78;
    ptRelCut = pow(8.0, 2);
    isoCut = 0.12;

    if (year_ == Year::yr2016) {
        ptRatioCut = 0.8;
        ptRelCut = pow(7.2, 2);
        mva.setup(fReader, "Electron_mvaSpring16GP");
        mvaLoose = { { -0.46, -0.48, 0, -0.85 },
                     { -0.03, -0.67, 0, -0.91 },
                     { 0.06, -0.49, 0, -0.83 } };
        mvaTight = { { 10, 0.77, 0, 0.52 }, { 10, 0.56, 0, 0.11 }, { 10, 0.48, 0, -0.01 } };
        /// Setup interpolation used for 25>pt>15
        for (size_t i = 0; i < mvaLoose.size(); i++) {
            mvaLoose[i][2] = (mvaLoose[i][3] - mvaLoose[i][1]) / 10;
            mvaTight[i][2] = (mvaTight[i][3] - mvaTight[i][1]) / 10;
        }
    } else if (year_ == Year::yr2017) {
        mva.setup(fReader, "Electron_mvaFall17V1noIso");
        mvaLoose = { { 0.488, -0.738667, 0.00986667, -0.64 },
                     { -0.045, -0.825, 0.005, -0.775 },
                     { 0.176, -0.784333, 0.00513333, -0.733 } };
        mvaTight = { { 10, 0.36, 0.032, 0.68 },
                     { 10, 0.225, 0.025, 0.475 },
                     { 10, 0.04, 0.028, 0.32 } };
    } else if (year_ == Year::yr2018) {
        mva.setup(fReader, "Electron_mvaFall17V2noIso");
        mvaLoose = { { 1.32, 0.544, 0.066, 1.204 },
                     { 0.192, -0.246, 0.033, 0.084 },
                     { 0.362, -0.653, 0.053, -0.123 } };
        mvaTight = { { 100, 3.157, 0.112, 4.277 },
                     { 100, 2.552, 0.06, 3.152 },
                     { 100, 1.489, 0.087, 2.359 } };
    }

    setSF<TH2F>("ElectronSF_low", Systematic::Electron_SF);
    setSF<TH2F>("ElectronSF", Systematic::Electron_SF);
    setSF<TH2F>("Electron_MVATightIP2D3DIDEmu", Systematic::Electron_Susy);
    setSF<TH2F>("Electron_ConvIHit0", Systematic::Electron_Susy);
    setSF<TH2F>("Electron_MultiIsoEmu", Systematic::Electron_Susy);
}

void Electron::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 7
            && fabs(eta(i)) < 2.5
            && convVeto.at(i)
            && lostHits.at(i) <= 1
            && fabs(dz.at(i)) < 0.1 && fabs(dxy.at(i)) < 0.05
            && passMVACut(i, false)
            && iso.at(i) < 0.4
            && fabs(eInvMinusPInv.at(i) < 0.01)
            && hoe.at(i) < 0.08
            && ((fabs(eta(i)) < BARREL_ETA && sieie.at(i) < 0.011) || (fabs(eta(i)) >= BARREL_ETA && sieie.at(i) < 0.031)))
            m_partList[Level::Loose]->push_back(i);
    }
}

/// closejet w iso
void Electron::createFakeList(Particle& jets)
{
    for (auto i : list(Level::Loose)) {
        if (sip3d.at(i) < 4
            && lostHits.at(i) == 0
            && tightCharge.at(i) == 2) {
            auto closejet_info = getCloseJet(i, jets);
            fakePtFactor[i] = fillFakePt(i, jets);
            if (getModPt(i) > 10) {
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
            && iso.at(i) < isoCut
            && ecalSumEt.at(i) / pt(i) < 0.45
            && hcalSumEt.at(i) / pt(i) < 0.25
            && tkSumPt.at(i) / pt(i) < 0.2
            && passMVACut(i, true)
            && passJetIsolation(i, jets))
            m_partList[Level::Tight]->push_back(i);
    }
}

bool Electron::passMVACut(size_t idx, bool isTight)
{
    int caseIdx = 0;

    //// ETA Splitting
    if (pt(idx) < 5)
        return false;
    else if (fabs(eta(idx)) < 0.8)
        caseIdx = 0;
    else if (fabs(eta(idx)) < BARREL_ETA)
        caseIdx = 1;
    else
        caseIdx = 2;
    auto& mvaCuts = (isTight) ? mvaTight[caseIdx] : mvaLoose[caseIdx];

    //// PT Splitting
    if (pt(idx) < 10)
        caseIdx = 0;
    else if (pt(idx) < 15 && year_ == Year::yr2016)
        caseIdx = 1;
    else if (pt(idx) < 25)
        caseIdx = 2;
    else
        caseIdx = 3;

    double mvaValue = mva.at(idx);
    if (year_ == Year::yr2018)
        mvaValue = atanh(mva.at(idx));

    if (caseIdx % 4 != 2)
        return mvaValue > mvaCuts[caseIdx % 4];
    else
        return mvaValue > mvaCuts[1] + mvaCuts[2] * (pt(idx) - 15);
}

float Electron::getScaleFactor()
{
    float weight = 1.;
    for (auto eidx : list(Level::Tight)) {
        float fixed_pt = std::min(pt(eidx), ptMax);
        if (fixed_pt < 20) {
            weight *= getWeight("ElectronSF_low", eta(eidx), fixed_pt);
        } else {
            weight *= getWeight("ElectronSF", eta(eidx), fixed_pt);
        }
        weight *= getWeight("Electron_MVATightIP2D3DIDEmu", eta(eidx), fixed_pt);
        weight *= getWeight("Electron_ConvIHit0", eta(eidx), fixed_pt);
        weight *= getWeight("Electron_MultiIsoEmu", eta(eidx), fixed_pt);
    }
        return weight;
}
