#ifndef __MUON_H_
#define __MUON_H_

#include "analysis_suite/Analyzer/interface/Lepton.h"

class Muon : public Lepton {
public:
    void setup(TTreeReader& fReader);
    virtual void createLooseList() override;
    virtual void createFakeList(Particle& jets) override;
    virtual void createTightList(Particle& jets) override;
    virtual float getScaleFactor() override;

    TTRArray<Bool_t>* isGlobal;
    TTRArray<Bool_t>* isTracker;
    TTRArray<Bool_t>* isPFcand;
    TTRArray<Float_t>* iso;
    TTRArray<Float_t>* dz;
    TTRArray<Float_t>* dxy;
    TTRArray<Int_t>* tightCharge;
    TTRArray<Bool_t>* mediumId;
    TTRArray<Float_t>* sip3d;

    Float_t ptMax = 119;
    Float_t ptMin = 20;
};

#endif // __MUON_H_
