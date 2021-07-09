#ifndef THREETOP_H
#define THREETOP_H

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/GenParticle.h"
#include "analysis_suite/Analyzer/interface/Output.h"
#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

template <class T>
using TTRValue = TTreeReaderValue<T>;

enum class Channel {
    Hadronic,
    Single,
    OS,
    SS,
    Multi
};

enum class Subchannel {
    MM,
    EM,
    ME,
    EE,
};

class ThreeTop : public BaseSelector {
public:
    virtual void Init(TTree* tree) override;
    virtual bool passSelection() override;
    virtual void FillValues(const std::vector<bool>& passVec) override;
    virtual void SetupOutTreeBranches(TTree* tree) override;
    virtual void setupChannel() override;
    virtual void ApplyScaleFactors() override;
    virtual void clearValues() override;
    virtual void setOtherGoodParticles(size_t syst) override;
    virtual void fillCutFlow() override;
    ClassDefOverride(ThreeTop, 0);

private:
    void printStuff();
    float getLeadPt();
    Subchannel subChannel_;

    TTree* treeFakeRate_;

    ResolvedTop rTop;
    GenParticle rGen;

    ParticleOut* o_looseMuons;
    ParticleOut* o_tightMuons;
    ParticleOut* o_looseElectrons;
    ParticleOut* o_tightElectrons;
    ParticleOut* o_tightLeptons;
    ParticleOut* o_jets;
    BJetOut* o_bJets;
    TopOut* o_resolvedTop;

    TTRValue<ULong64_t>* event;
    TTRValue<Bool_t>* Flag_goodVertices;
    TTRValue<Bool_t>* Flag_globalSuperTightHalo2016Filter;
    TTRValue<Bool_t>* Flag_HBHENoiseFilter;
    TTRValue<Bool_t>* Flag_HBHENoiseIsoFilter;
    TTRValue<Bool_t>* Flag_EcalDeadCellTriggerPrimitiveFilter;
    TTRValue<Bool_t>* Flag_BadPFMuonFilter;
    TTRValue<Bool_t>* Flag_ecalBadCalibFilter;
    TTRValue<Float_t>* Met_pt;
    TTRValue<Float_t>* Met_phi;
    TTRValue<Float_t>* Pileup_nTrueInt;

    TTRValue<Bool_t>*HLT_MuMu, *HLT_MuEle, *HLT_EleMu, *HLT_EleEle;

    std::vector<Float_t> o_ht, o_htb, o_met, o_metphi, o_centrality;

    TH2F *passTrigger_leadPt, *failTrigger_leadPt;
    TH1F *cutFlow, *cutFlow_individual;
    bool cutFlows_setBins = false;
};

#endif
