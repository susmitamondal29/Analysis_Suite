#ifndef THREETOP_H
#define THREETOP_H

#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "analysis_suite/Analyzer/interface/ResolvedTop.h"
#include <map>

template<class T>
using TTRValue = TTreeReaderValue<T>;

class ThreeTop : public BaseSelector {
    public:
        virtual void Init(TTree* tree) override;
        virtual bool passSelection(int variation) override;
        virtual void FillValues(int variation) override;
        virtual void SetupOutTree() override;
        virtual void setupChannel() override;
        virtual void ApplyScaleFactors() override;
                virtual void clearValues() override;
                virtual void setupParticles() override;
                ClassDefOverride(ThreeTop, 0);

    private:
        void FillLeptons();

                ResolvedTop rTop;

                ParticleOut* o_looseMuons;
        ParticleOut* o_tightMuons;
        ParticleOut* o_looseElectrons;
        ParticleOut* o_tightElectrons;
        ParticleOut* o_tightLeptons;
        ParticleOut* o_jets;
                BJetOut* o_bJets;
                TopOut* o_resolvedTop;

                TTRValue<Bool_t>* Flag_goodVertices;
        TTRValue<Bool_t>* Flag_globalSuperTightHalo2016Filter;
        TTRValue<Bool_t>* Flag_HBHENoiseFilter;
        TTRValue<Bool_t>* Flag_HBHENoiseIsoFilter;
        TTRValue<Bool_t>* Flag_EcalDeadCellTriggerPrimitiveFilter;
        TTRValue<Bool_t>* Flag_BadPFMuonFilter;
        TTRValue<Bool_t>* Flag_ecalBadCalibFilter;
        TTRValue<Float_t>* Met_pt;
        TTRValue<Float_t>* Met_phi;

                float o_ht, o_htb, o_met, o_metphi, o_centrality;
};

#endif
