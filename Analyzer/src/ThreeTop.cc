#include "analysis_suite/Analyzer/interface/ThreeTop.h"

enum CHANNELS {CHAN_HAD, CHAN_SINGLE, CHAN_OS, CHAN_SS, CHAN_MULTI};


void ThreeTop::Init(TTree *tree) {
    channel_ = CHAN_SS;
    BaseSelector::Init(tree);
         
    Flag_goodVertices = new TTRValue<Bool_t>(fReader, "Flag_goodVertices");
    Flag_globalSuperTightHalo2016Filter = new TTRValue<Bool_t>(fReader, "Flag_globalSuperTightHalo2016Filter");
    Flag_HBHENoiseFilter = new TTRValue<Bool_t>(fReader, "Flag_HBHENoiseFilter");
    Flag_HBHENoiseIsoFilter = new TTRValue<Bool_t>(fReader, "Flag_HBHENoiseIsoFilter");
    Flag_EcalDeadCellTriggerPrimitiveFilter = new TTRValue<Bool_t>(fReader, "Flag_EcalDeadCellTriggerPrimitiveFilter");
    Flag_BadPFMuonFilter = new TTRValue<Bool_t>(fReader, "Flag_BadPFMuonFilter");
    Flag_ecalBadCalibFilter = new TTRValue<Bool_t>(fReader, "Flag_ecalBadCalibFilter");
    Met_pt = new TTRValue<Float_t>(fReader, "MET_pt");
    Met_phi = new TTRValue<Float_t>(fReader, "MET_phi");
}

void ThreeTop::SetupOutTree() {
    outTree->Branch("LooseMuon", "ParticleOut", &o_looseMuons);
    outTree->Branch("TightMuon", "ParticleOut", &o_tightMuons);
    outTree->Branch("LooseElectron", "ParticleOut", &o_looseElectrons);
    outTree->Branch("TightElectron", "ParticleOut", &o_tightElectrons);
    outTree->Branch("Jets", "ParticleOut", &o_jets);
    outTree->Branch("BJets", "ParticleOut", &o_bJets);

    outTree->Branch("HT", &o_ht, "HT/F");
    outTree->Branch("HT_b", &o_htb, "HT_b/F");
    outTree->Branch("Met", &o_met, "Met/F");
    outTree->Branch("Met_phi", &o_metphi, "Met_phi/F");
    outTree->Branch("Centrality", &o_centrality, "Centrality/F");

}

/// Make to seperate fuctionality
void ThreeTop::clearValues() {
    muon.clear();
    elec.clear();
    jet.clear();
    
    o_looseMuons->clear();
    o_tightMuons->clear();
    o_looseElectrons->clear();
    o_tightElectrons->clear();
    o_jets->clear();
    o_bJets->clear();
}

void ThreeTop::ApplyScaleFactors() {

}

void ThreeTop::setupChannel() {
    size_t nLep = muon.tightList.size() + elec.tightList.size();
    if (nLep == 0)
        currentChannel_ = CHAN_HAD;
    else if (nLep == 1)
        currentChannel_ = CHAN_SINGLE;
    else if (nLep == 2) {
        int q_product = 1;
        for(auto i: elec.tightList)
            q_product *= elec.charge->At(i);
        for(auto i: muon.tightList)
            q_product *= muon.charge->At(i);
        if (q_product > 0)
            currentChannel_ = CHAN_SS;
        else
            currentChannel_ = CHAN_OS;
    } else
        currentChannel_ = CHAN_MULTI;

}


bool ThreeTop::passSelection(int variation) {
    bool passMETFilter = (**Flag_goodVertices
                       && **Flag_globalSuperTightHalo2016Filter
                       && **Flag_HBHENoiseFilter
                       && **Flag_HBHENoiseIsoFilter
                       && **Flag_EcalDeadCellTriggerPrimitiveFilter
                       && **Flag_BadPFMuonFilter
                       && **Flag_ecalBadCalibFilter);
    bool passZVeto = muon.passZVeto() && elec.passZVeto();
    bool passChannel = currentChannel_ == channel_;
    bool passJetNumber = jet.tightList.size() >= 2;
    bool passBJetNumber = jet.tightList.size() >= 1;
    bool passMetCut = **Met_pt > 25;
    bool passHTCut = jet.getHT(jet.tightList) > 250;

    return (passMETFilter &&
       passMetCut &&
       passZVeto &&
       passChannel &&
       passJetNumber &&
       passBJetNumber &&
       passHTCut
    );
    

}

void ThreeTop::FillValues(int variation) {
    muon.fillParticle(muon.looseList, *o_looseMuons);
    muon.fillParticle(muon.tightList, *o_tightMuons);
    elec.fillParticle(elec.looseList, *o_looseElectrons);
    elec.fillParticle(elec.looseList, *o_tightElectrons);
    jet.fillParticle(jet.tightList, *o_jets);
    jet.fillParticle(jet.bjetList, *o_bJets);

    o_ht = jet.getHT(jet.tightList);
    o_htb = jet.getHT(jet.bjetList);
    o_met = **Met_pt;
    o_metphi = **Met_phi;
    o_centrality = jet.getCentrality(jet.tightList);
}
