#ifndef FAKERATE_H_
#define FAKERATE_H_

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/Output.h"

#include <set>

class FakeRate : public BaseSelector {
public:
    virtual void Init(TTree* tree) override;
    virtual bool getCutFlow() override;
    virtual void FillValues(const std::vector<bool>& passVec) override;
    virtual void SetupOutTreeBranches(TTree* tree) override;
    virtual void ApplyScaleFactors() override;
    void ApplyDataSpecifics();
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
    bool isSameSign();

    LeptonOut_Fake* o_fakeMuons;
    LeptonOut_Fake* o_tightMuons;
    LeptonOut_Fake* o_fakeElectrons;
    LeptonOut_Fake* o_tightElectrons;
    JetOut* o_jets;
    JetOut* o_bJets;

    TRVariable<Float_t> Pileup_nTrueInt;

    std::vector<Float_t> o_ht, o_htb, o_met, o_metphi;
    std::vector<size_t> o_nb_loose, o_nb_tight;

    std::set<std::string> ewk_sets = {"ttjet", "ttbar", "wjets", "DYm50", "DYm10-50",
                                      "ttbar_2l2n", "ttbar_semilep", "ttbar_hadronic",
                                      "DYm50_amc",
    };

    LorentzVector lead_lep;
};


#endif // FAKERATE_H_
