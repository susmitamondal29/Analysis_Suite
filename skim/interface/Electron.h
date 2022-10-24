#ifndef __ELECTRON_H_
#define __ELECTRON_H_

#include "analysis_suite/skim/interface/Lepton.h"

class Electron : public Lepton {
public:
    void setup(TTreeReader& fReader);
    virtual void createLooseList() override;
    // virtual void createFakeList(Particle& jets) override;
    virtual void createTightList(Particle& jets) override;
    virtual float getScaleFactor() override;

    // Float_t pt(size_t idx) const { return m_pt.at(idx) / eCorr.at(idx); };
    // Float_t pt(Level level, size_t i) const { return pt(idx(level, i)); }

    TRArray<Float_t> eCorr;
    TRArray<UChar_t> lostHits;
    TRArray<Bool_t> convVeto;
    TRArray<Float_t> sieie;
    TRArray<Float_t> hoe;
    TRArray<Float_t> eInvMinusPInv;
    TRArray<Float_t> mva;
    TRArray<Int_t> tightCharge;
    TRArray<Float_t> ecalSumEt;
    TRArray<Float_t> hcalSumEt;
    TRArray<Float_t> tkSumPt;

    TRArray<Bool_t> mva_l;
    TRArray<Bool_t> mva_80;
    TRArray<Bool_t> mva_90;

private:
    bool passTriggerRequirements(size_t i);

    const float BARREL_ETA = 1.479;
    WeightHolder electron_scale;
};

#endif // __ELECTRON_H_
