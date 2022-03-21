#ifndef FAKERATE_H_
#define FAKERATE_H_

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/Output.h"

class FakeRate : public BaseSelector {
public:
    virtual void Init(TTree* tree) override;
    virtual bool getCutFlow() override;
    virtual void FillValues(const std::vector<bool>& passVec) override;
    virtual void SetupOutTreeBranches(TTree* tree) override;
    virtual void ApplyScaleFactors() override;
    virtual void clearParticles() override;
    virtual void clearOutputs() override;
    virtual void setOtherGoodParticles(size_t syst) override;
    ClassDefOverride(FakeRate, 0);

private:
    void setSubChannel();
    void set_leadlep();
    bool measurement_cuts();
    bool sideband_cuts();
    bool closure_cuts();
    bool single_lep_cuts(CutInfo& cuts);

    float getLeadPt();

    TTree* treeFakeRate_;

    ParticleOut* o_looseMuons;
    ParticleOut* o_tightMuons;
    ParticleOut* o_looseElectrons;
    ParticleOut* o_tightElectrons;
    JetOut* o_jets;
    BJetOut* o_bJets;

    TRVariable<Float_t> Met_pt;
    TRVariable<Float_t> Met_phi;
    TRVariable<Float_t> Pileup_nTrueInt;

    std::vector<Float_t> o_ht, o_htb, o_met, o_metphi;


    LorentzVector lead_lep;
};


#endif // FAKERATE_H_
