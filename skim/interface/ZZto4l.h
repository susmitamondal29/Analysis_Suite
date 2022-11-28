#ifndef ZZANALYSIS_H
#define ZZANALYSIS_H

#include "analysis_suite/skim/interface/BaseSelector.h"
#include "analysis_suite/skim/interface/Output.h"
#include "analysis_suite/skim/interface/ZBoson.h"

class ZZto4l : public BaseSelector {
public:
    void Init(TTree* tree) override;
    bool getCutFlow() override;
    void FillValues(const Bitmap& event_bitmap) override;
    void SetupOutTreeBranches(TTree* tree) override;
    void ApplyScaleFactors() override;
    void clearParticles() override;
    void clearOutputs() override;
    void setOtherGoodParticles(size_t syst) override;
    ClassDefOverride(ZZto4l, 0);

private:
    void ApplyDataScaleFactors();
    void printStuff();
    void setSubChannel();

    bool signal_cuts();

    float muPt(size_t idx) { return muon.size(Level::Tight) > idx ? muon.pt(Level::Tight, idx) : -1; }
    float elPt(size_t idx) { return elec.size(Level::Tight) > idx ? elec.pt(Level::Tight, idx) : -1; }

    ZBoson z_ee, z_mu;

    ParticleOut* o_Z_ee;
    ParticleOut* o_Z_mm;

    TRVariable<Float_t> Pileup_nTrueInt;

    // TrigEff trigEff_leadPt;

};

#endif
