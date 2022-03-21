#ifndef THREETOP_H
#define THREETOP_H

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/Output.h"
#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

class ThreeTop : public BaseSelector {
public:
    virtual void Init(TTree* tree) override;
    virtual bool getCutFlow() override;
    virtual void FillValues(const std::vector<bool>& passVec) override;
    virtual void SetupOutTreeBranches(TTree* tree) override;
    virtual void ApplyScaleFactors() override;
    virtual void clearParticles() override;
    virtual void clearOutputs() override;
    virtual void setOtherGoodParticles(size_t syst) override;
    ClassDefOverride(ThreeTop, 0);

private:
    void printStuff();
    float getLeadPt(size_t idx = 0);
    void setSubChannel();
    bool isSameSign(Level level);

    bool baseline_cuts(CutInfo& cuts);
    bool signal_cuts();
    bool nonprompt_cuts();
    bool charge_misid_cuts();
    bool ttz_CR_cuts();

    float muPt(size_t idx) { return muon.size(Level::Tight) > idx ? muon.pt(Level::Tight, idx) : -1; }
    float elPt(size_t idx) { return elec.size(Level::Tight) > idx ? elec.pt(Level::Tight, idx) : -1; }

    ResolvedTop rTop;

    ParticleOut* o_looseMuons;
    ParticleOut* o_looseElectrons;
    LeptonOut* o_tightMuons;
    LeptonOut* o_tightElectrons;
    ParticleOut* o_tightLeptons;
    JetOut* o_jets;
    BJetOut* o_bJets;
    TopOut* o_resolvedTop;

    TRVariable<ULong64_t> event;
    TRVariable<Float_t> Met_pt;
    TRVariable<Float_t> Met_phi;
    TRVariable<Float_t> Pileup_nTrueInt;

    std::vector<Float_t> o_ht, o_htb, o_met, o_metphi, o_centrality;

    TrigEff trigEff_leadPt;

    std::set<std::string> chargeMis_list = {"DYm50", "DY10-50", "ttbar"};
};

#endif
