#ifndef LEPTON_MISID_CLOSURE_H_
#define LEPTON_MISID_CLOSURE_H_

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/Output.h"

class Closure_MisId : public BaseSelector {
 public:
    virtual void Init(TTree* tree) override;
    virtual bool getCutFlow() override;
    virtual void FillValues(const std::vector<bool>& passVec) override;
    virtual void SetupOutTreeBranches(TTree* tree) override;
    virtual void ApplyScaleFactors() override;
    virtual void clearParticles() override;
    virtual void clearOutputs() override;
    ClassDefOverride(Closure_MisId, 0);

 private:
    void printStuff();
    bool isSameSign();
    bool measurement_cuts();
    bool closure_cuts();
    void setSubChannel();
    float getLeadPt();
    float get_mass();
    void set_LHELeps();

    TTree* treeFakeRate_;

    LeptonOut* o_tightMuons;
    LeptonOut* o_tightElectrons;
    JetOut* o_jets;

    TRVariable<Float_t> Met_pt;
    TRVariable<Float_t> Met_phi;
    TRVariable<Float_t> Pileup_nTrueInt;
    TRVariable<Float_t> LHE_HT;
    TRArray<Int_t> LHE_pdgId;

    size_t nLHE_leps;

    std::vector<Float_t> o_ht, o_ht_lhe, o_htb, o_met, o_metphi, o_centrality, o_nlhe_leps;
};

#endif // LEPTON_MISID_CLOSURE_H_
