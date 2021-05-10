#include "analysis_suite/Analyzer/interface/ThreeTop.h"

#define getElec(var, i) (elec.var->At(elec.tightList->at(i)))
#define getMuon(var, i) (muon.var->At(muon.tightList->at(i)))

enum CHANNELS { CHAN_HAD,
    CHAN_SINGLE,
    CHAN_OS,
    CHAN_SS,
    CHAN_MULTI };

enum SUBCHANNELS {
    CHAN_MM,
    CHAN_EM,
    CHAN_ME,
    CHAN_EE,
};

void ThreeTop::Init(TTree* tree)
{
    channel_ = CHAN_SS;
    BaseSelector::Init(tree);

    passTrigger_leadPt = new TH2F("passTrigger", "passTrigger", 4, 0, 4, 100, 0, 100);
    fOutput->Add(passTrigger_leadPt);
    failTrigger_leadPt = new TH2F("failTrigger", "failTrigger", 4, 0, 4, 100, 0, 100);
    fOutput->Add(failTrigger_leadPt);
    cutFlow = new TH1F("cutFlow", "cutFlow", 15, 0, 15);
    fOutput->Add(cutFlow);
    cutFlow_individual = new TH1F("cutFlow_individual", "cutFlow_individual", 15, 0, 15);
    fOutput->Add(cutFlow_individual);

    rTop.setup(fReader, year_);
    rGen.setup(fReader, year_, isMC_);

    event = new TTRValue<ULong64_t>(fReader, "event");
    Flag_goodVertices = new TTRValue<Bool_t>(fReader, "Flag_goodVertices");
    Flag_globalSuperTightHalo2016Filter = new TTRValue<Bool_t>(fReader, "Flag_globalSuperTightHalo2016Filter");
    Flag_HBHENoiseFilter = new TTRValue<Bool_t>(fReader, "Flag_HBHENoiseFilter");
    Flag_HBHENoiseIsoFilter = new TTRValue<Bool_t>(fReader, "Flag_HBHENoiseIsoFilter");
    Flag_EcalDeadCellTriggerPrimitiveFilter = new TTRValue<Bool_t>(fReader, "Flag_EcalDeadCellTriggerPrimitiveFilter");
    Flag_BadPFMuonFilter = new TTRValue<Bool_t>(fReader, "Flag_BadPFMuonFilter");
    Flag_ecalBadCalibFilter = new TTRValue<Bool_t>(fReader, "Flag_ecalBadCalibFilter");
    Met_pt = new TTRValue<Float_t>(fReader, "MET_pt");
    Met_phi = new TTRValue<Float_t>(fReader, "MET_phi");
    Pileup_nTrueInt = new TTRValue<Float_t>(fReader, "Pileup_nTrueInt");

    //HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8
    HLT_MuMu = new TTRValue<Bool_t>(fReader, "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
    HLT_MuEle = new TTRValue<Bool_t>(fReader, "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL");
    HLT_EleMu = new TTRValue<Bool_t>(fReader, "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL");
    HLT_EleEle = new TTRValue<Bool_t>(fReader, "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL");
}

void ThreeTop::SetupOutTree()
{
    outTree->Branch("LooseMuon", "ParticleOut", &o_looseMuons);
    outTree->Branch("TightMuon", "ParticleOut", &o_tightMuons);
    outTree->Branch("LooseElectron", "ParticleOut", &o_looseElectrons);
    outTree->Branch("TightElectron", "ParticleOut", &o_tightElectrons);
    outTree->Branch("TightLeptons", "ParticleOut", &o_tightLeptons);
    outTree->Branch("Jets", "ParticleOut", &o_jets);
    outTree->Branch("BJets", "BJetOut", &o_bJets);
    outTree->Branch("ResolvedTops", "TopOut", &o_resolvedTop);

    outTree->Branch("HT", &o_ht, "HT/F");
    outTree->Branch("HT_b", &o_htb, "HT_b/F");
    outTree->Branch("Met", &o_met, "Met/F");
    outTree->Branch("Met_phi", &o_metphi, "Met_phi/F");
    outTree->Branch("Centrality", &o_centrality, "Centrality/F");
}

/// Make to seperate fuctionality
void ThreeTop::clearValues()
{
    muon.clear();
    elec.clear();
    jet.clear();
    rTop.clear();
    rGen.clear();

    o_looseMuons->clear();
    o_tightMuons->clear();
    o_looseElectrons->clear();
    o_tightElectrons->clear();
    o_tightLeptons->clear();
    o_jets->clear();
    o_bJets->clear();
    o_resolvedTop->clear();
}

void ThreeTop::ApplyScaleFactors()
{
    weight *= sfMaker.getBJetSF(jet);
    weight *= sfMaker.getPileupSF(**Pileup_nTrueInt);
    weight *= sfMaker.getResolvedTopSF(rTop, rGen);
    weight *= sfMaker.getElectronSF(elec);
    weight *= sfMaker.getMuonSF(muon);
}

void ThreeTop::setOtherGoodParticles(size_t syst)
{
    rTop.setGoodParticles(syst);
    rGen.setGoodParticles(syst);
}

void ThreeTop::setupChannel()
{
    size_t nLep = muon.tightList->size() + elec.tightList->size();
    if (nLep == 0)
        currentChannel_ = CHAN_HAD;
    else if (nLep == 1)
        currentChannel_ = CHAN_SINGLE;
    else if (nLep == 2) {
        int q_product = 1;
        if (elec.tightList->size() == 2) {
            subChannel_ = CHAN_EE;
            q_product *= getElec(charge, 0) * getElec(charge, 1);
        } else if (muon.tightList->size() == 2) {
            subChannel_ = CHAN_MM;
            q_product *= getMuon(charge, 0) * getMuon(charge, 1);
        } else {
            q_product *= getMuon(charge, 0) * getElec(charge, 0);
            subChannel_ = (getMuon(pt, 0) > getElec(pt, 0)) ? CHAN_ME : CHAN_EM;
        }
        // Set Dilepton channel
        if (q_product > 0)
            currentChannel_ = CHAN_SS;
        else
            currentChannel_ = CHAN_OS;
    } else
        currentChannel_ = CHAN_MULTI;
}

bool ThreeTop::passSelection()
{
    std::vector<std::pair<std::string, bool>> cuts;
    cuts.push_back(std::make_pair("passPreselection", true));

    cuts.push_back(std::make_pair("passMETFilter",
        (**Flag_goodVertices && **Flag_globalSuperTightHalo2016Filter && **Flag_HBHENoiseFilter && **Flag_HBHENoiseIsoFilter && **Flag_EcalDeadCellTriggerPrimitiveFilter && **Flag_BadPFMuonFilter && **Flag_ecalBadCalibFilter)));
    cuts.push_back(std::make_pair("passZVeto",
        muon.passZVeto() && elec.passZVeto()));
    cuts.push_back(std::make_pair("passChannel",
        currentChannel_ == channel_));
    cuts.push_back(std::make_pair("passJetNumber",
        jet.tightList->size() >= 2));
    cuts.push_back(std::make_pair("passBJetNumber",
        jet.bjetList->size() >= 1));
    cuts.push_back(std::make_pair("passMetCut",
        **Met_pt > 25));
    cuts.push_back(std::make_pair("passHTCut",
        jet.getHT(jet.tightList) > 250));

    return fillCutFlow(cuts);
}

bool ThreeTop::fillCutFlow(std::vector<std::pair<std::string, bool>> cuts)
{
    if (!cutFlows_setBins) {
        cutFlows_setBins = true;
        int i = 1;
        for (auto cut : cuts) {
            cutFlow->GetXaxis()->SetBinLabel(i, cut.first.c_str());
            cutFlow_individual->GetXaxis()->SetBinLabel(i, cut.first.c_str());
            i++;
        }
    }

    bool passAll = true;
    for (auto cut : cuts) {
        bool truth = cut.second;
        passAll &= truth;
        if (truth)
            cutFlow_individual->Fill(cut.first.c_str(), weight);
        if (passAll)
            cutFlow->Fill(cut.first.c_str(), weight);
    }
    return passAll;
}

bool ThreeTop::passTrigger()
{
    bool passLeadPt = true; //getLeadPt() > 25;
    bool passTrig = false;
    if (subChannel_ == CHAN_MM)
        passTrig = **HLT_MuMu;
    else if (subChannel_ == CHAN_EM)
        passTrig = **HLT_EleMu;
    else if (subChannel_ == CHAN_ME)
        passTrig = **HLT_MuEle;
    else if (subChannel_ == CHAN_EE)
        passTrig = **HLT_EleEle;

    if (passTrig) {
        passTrigger_leadPt->Fill(subChannel_, getLeadPt(), weight);
    } else {
        failTrigger_leadPt->Fill(subChannel_, getLeadPt(), weight);
    }

    return (passLeadPt && passTrig);
}

void ThreeTop::FillValues(std::vector<bool> passVec)
{
    fillParticle(muon, muon.looseArray, *o_looseMuons);
    fillParticle(muon, muon.tightArray, *o_tightMuons);
    fillParticle(elec, elec.looseArray, *o_looseElectrons);
    fillParticle(elec, elec.tightArray, *o_tightElectrons);
    fillParticle(jet, jet.tightArray, *o_jets);
    fillBJet(jet, jet.bjetArray, *o_bJets);
    fillTop(rTop, rTop.looseArray, *o_resolvedTop);
    // fillLeptons(muon, elec, *o_tightLeptons);

    o_ht = jet.getHT(jet.tightList);
    o_htb = jet.getHT(jet.bjetList);
    o_met = **Met_pt;
    o_metphi = **Met_phi;
    o_centrality = jet.getCentrality(jet.tightList);
}

float ThreeTop::getLeadPt()
{
    if (channel_ != CHAN_SS)
        return 0.;
    else if (subChannel_ % 2 == 0)
        return getMuon(pt, 0);
    else
        return getElec(pt, 0);
}

void ThreeTop::printStuff()
{
    std::cout << "Event: " << **event << std::endl;
    std::cout << "Met: " << **Met_pt << std::endl;
    std::cout << "HT: " << jet.getHT(jet.tightList) << std::endl;
    std::cout << "njet: " << jet.tightList->size() << std::endl;
    std::cout << "nbjet: " << jet.bjetList->size() << std::endl;
    std::cout << "nlep: " << muon.tightList->size() << " " << elec.tightList->size() << std::endl;
    std::cout << "lepVeto: " << muon.passZVeto() << " " << elec.passZVeto() << std::endl;
    std::cout << std::endl;
}
