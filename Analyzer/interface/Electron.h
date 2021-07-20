#ifndef __ELECTRON_H_
#define __ELECTRON_H_

#include "analysis_suite/Analyzer/interface/Lepton.h"

class Electron : public Lepton {
public:
    void setup(TTreeReader& fReader);
    virtual void createLooseList() override;
    virtual void createFakeList(Particle& jets) override;
    virtual void createTightList(Particle& jets) override;
    virtual float getScaleFactor() override;

    Float_t pt(size_t idx) { return m_pt->At(idx) / eCorr->At(idx); };

    TTRArray<Float_t>* eCorr;
    TTRArray<UChar_t>* lostHits;
    TTRArray<Bool_t>* convVeto;
    TTRArray<Float_t>* iso;
    TTRArray<Float_t>* dz;
    TTRArray<Float_t>* dxy;
    TTRArray<Float_t>* sieie;
    TTRArray<Float_t>* hoe;
    TTRArray<Float_t>* eInvMinusPInv;
    TTRArray<Float_t>* sip3d;
    TTRArray<Float_t>* mva;
    TTRArray<Int_t>* tightCharge;
    TTRArray<Float_t>* ecalSumEt;
    TTRArray<Float_t>* hcalSumEt;
    TTRArray<Float_t>* tkSumPt;

private:
    const float BARREL_ETA = 1.479;
    std::vector<std::vector<double>> mvaLoose, mvaTight;
    bool passMVACut(size_t idx, bool isTight);

    TH2F *electronLowSF, *electronSF, *electronSusySF;
    Float_t ptMax = 499;
};

#endif // __ELECTRON_H_
