#ifndef __MUON_H_
#define __MUON_H_

#include "analysis_suite/skim/interface/Lepton.h"
#include "analysis_suite/skim/interface/RoccoR.h"

class Muon : public Lepton {
public:
    void setup(TTreeReader& fReader);
    virtual void createLooseList() override;
    // virtual void createFakeList(Particle& jets) override;
    virtual void createTightList(Particle& jets) override;
    virtual float getScaleFactor() override;

    float getRocCorrection(GenParticle& gen);

    TRArray<Bool_t> isGlobal;
    TRArray<Bool_t> isTracker;
    TRArray<Bool_t> isPFcand;
    TRArray<Int_t> tightCharge;
    TRArray<Bool_t> mediumId;
    TRArray<Int_t> nTrackerLayers;

    RoccoR roc_corr;

    WeightHolder muon_scale;

};

#endif // __MUON_H_
