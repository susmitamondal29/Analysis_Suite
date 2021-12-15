#ifndef FAKERATE_H_
#define FAKERATE_H_

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/Output.h"

class FakeRate : public BaseSelector {
public:
    virtual void Init(TTree* tree) override;
    virtual bool getCutFlow(cut_info& cuts) override;
    virtual bool getTriggerCut(cut_info& cuts) override;
    virtual void FillValues(const std::vector<bool>& passVec) override;
    virtual void SetupOutTreeBranches(TTree* tree) override;
    virtual void setupChannel() override;
    virtual void ApplyScaleFactors() override;
    virtual void clearParticles() override;
    virtual void clearOutputs() override;
    virtual void setOtherGoodParticles(size_t syst) override;
    ClassDefOverride(FakeRate, 0);

private:
    float getLeadPt(size_t idx = 0);
    void setSubChannel();

    Subchannel subChannel_;

    TTree* treeFakeRate_;


    LeptonOut* o_looseMuons;
    LeptonOut* o_tightMuons;
    LeptonOut* o_looseElectrons;
    LeptonOut* o_tightElectrons;
    JetOut* o_jets;
    BJetOut* o_bJets;

    TRVariable<ULong64_t> event;
    TRVariable<Bool_t> Flag_goodVertices;
    TRVariable<Bool_t> Flag_globalSuperTightHalo2016Filter;
    TRVariable<Bool_t> Flag_HBHENoiseFilter;
    TRVariable<Bool_t> Flag_HBHENoiseIsoFilter;
    TRVariable<Bool_t> Flag_EcalDeadCellTriggerPrimitiveFilter;
    TRVariable<Bool_t> Flag_BadPFMuonFilter;
    TRVariable<Bool_t> Flag_ecalBadCalibFilter;
    TRVariable<Float_t> Met_pt;
    TRVariable<Float_t> Met_phi;
    TRVariable<Float_t> Pileup_nTrueInt;

    std::vector<Float_t> o_ht, o_htb, o_met, o_metphi, o_mt;

};


#endif // FAKERATE_H_
