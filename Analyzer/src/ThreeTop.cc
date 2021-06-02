#include "analysis_suite/Analyzer/interface/ThreeTop.h"

#define getElec(var, i) (elec.var(elec.list(Level::Tight).at(i)))
#define getMuon(var, i) (muon.var(muon.list(Level::Tight).at(i)))

void ThreeTop::Init(TTree* tree)
{
    channel_ = Channel::SS;
    BaseSelector::Init(tree);

    createObject(passTrigger_leadPt, "passTrigger", 4, 0, 4, 100, 0, 100);
    createObject(failTrigger_leadPt, "failTrigger", 4, 0, 4, 100, 0, 100);
    createObject(cutFlow, "cutFlow", 15, 0, 15);
    createObject(cutFlow_individual, "cutFlow_individual", 15, 0, 15);

    rTop.setup(fReader);
    rGen.setup(fReader, isMC_);

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

    outTree->Branch("HT", &o_ht);
    outTree->Branch("HT_b", &o_htb);
    outTree->Branch("Met", &o_met);
    outTree->Branch("Met_phi", &o_metphi);
    outTree->Branch("Centrality", &o_centrality);
}

/// Make to seperate fuctionality
void ThreeTop::clearValues()
{
    BaseSelector::clearValues();
    rTop.clear();
    rGen.clear();

    o_ht.clear();
    o_htb.clear();
    o_met.clear();
    o_metphi.clear();
    o_centrality.clear();
}

void ThreeTop::ApplyScaleFactors()
{
    (*weight) *= sfMaker.getBJetSF(jet);
    (*weight) *= sfMaker.getPileupSF(**Pileup_nTrueInt);
    (*weight) *= elec.getScaleFactor();
    (*weight) *= muon.getScaleFactor();
    (*weight) *= rTop.getScaleFactor();
}

void ThreeTop::setOtherGoodParticles(size_t syst)
{
    rTop.setGoodParticles(syst);
    rGen.setGoodParticles(syst);
}

void ThreeTop::setupChannel()
{
    size_t nLep = muon.size(Level::Tight) + elec.size(Level::Tight);
    if (nLep == 0)
        currentChannel_ = Channel::Hadronic;
    else if (nLep == 1)
        currentChannel_ = Channel::Single;
    else if (nLep == 2) {
        int q_product = 1;
        if (elec.size(Level::Tight) == 2) {
            subChannel_ = Subchannel::EE;
            q_product *= getElec(charge, 0) * getElec(charge, 1);
        } else if (muon.size(Level::Tight) == 2) {
            subChannel_ = Subchannel::MM;
            q_product *= getMuon(charge, 0) * getMuon(charge, 1);
        } else {
            q_product *= getMuon(charge, 0) * getElec(charge, 0);
            subChannel_ = (getMuon(pt, 0) > getElec(pt, 0)) ? Subchannel::ME : Subchannel::EM;
        }
        // Set Dilepton channel
        if (q_product > 0)
            currentChannel_ = Channel::SS;
        else
            currentChannel_ = Channel::OS;
    } else
        currentChannel_ = Channel::Multi;
}

bool ThreeTop::passSelection()
{
    cuts.push_back(std::make_pair("passPreselection", true));

    cuts.push_back(std::make_pair("passMETFilter",
        (**Flag_goodVertices && **Flag_globalSuperTightHalo2016Filter && **Flag_HBHENoiseFilter && **Flag_HBHENoiseIsoFilter && **Flag_EcalDeadCellTriggerPrimitiveFilter && **Flag_BadPFMuonFilter && **Flag_ecalBadCalibFilter)));
    cuts.push_back(std::make_pair("passZVeto", muon.passZVeto() && elec.passZVeto()));
    cuts.push_back(std::make_pair("passChannel", currentChannel_ == channel_));
    cuts.push_back(std::make_pair("passJetNumber", jet.size(Level::Tight) >= 2));
    cuts.push_back(std::make_pair("passBJetNumber", jet.size(Level::Bottom) >= 1));
    cuts.push_back(std::make_pair("passMetCut", **Met_pt > 25));
    cuts.push_back(std::make_pair("passHTCut", jet.getHT(Level::Tight) > 300));

    // Trigger stuff
    passTrigger = true;
    // // passLeadPt stuff
    // if (subChannel_ == Subchannel::MM)
    //     passTrigger &= **HLT_MuMu;
    // else if (subChannel_ == Subchannel::EM)
    //     passTrigger &= **HLT_EleMu;
    // else if (subChannel_ == Subchannel::ME)
    //     passTrigger &= **HLT_MuEle;
    // else if (subChannel_ == Subchannel::EE)
    //     passTrigger &= **HLT_EleEle;

    for (auto& cut : cuts) {
        if (!cut.second)
            return false;
    }
    return passTrigger;
}

void ThreeTop::fillCutFlow()
{
    // Setup cutflow histogram
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
            cutFlow_individual->Fill(cut.first.c_str(), *weight);
        if (passAll)
            cutFlow->Fill(cut.first.c_str(), *weight);
    }

    if (passAll && passTrigger) {
        passTrigger_leadPt->Fill(static_cast<int>(subChannel_), getLeadPt(), *weight);
    } else if (passAll) {
        failTrigger_leadPt->Fill(static_cast<int>(subChannel_), getLeadPt(), *weight);
    }
}

void ThreeTop::FillValues(const std::vector<bool>& passVec)
{
    size_t pass_bitmap = 0;
    for (size_t i = 0; i < passVec.size(); ++i) {
        pass_bitmap += passVec.at(i) << i;
    }

    fillParticle(muon, Level::Loose, *o_looseMuons, pass_bitmap);
    fillParticle(muon, Level::Tight, *o_tightMuons, pass_bitmap);
    fillParticle(elec, Level::Loose, *o_looseElectrons, pass_bitmap);
    fillParticle(elec, Level::Tight, *o_tightElectrons, pass_bitmap);
    fillParticle(jet, Level::Tight, *o_jets, pass_bitmap);
    fillBJet(jet, Level::Bottom, *o_bJets, pass_bitmap);
    fillTop(rTop, Level::Loose, *o_resolvedTop, pass_bitmap);
    fillLeptons(muon, elec, *o_tightLeptons, pass_bitmap);

    for (size_t syst = 0; syst < numSystematics(); ++syst) {
        o_ht.push_back(jet.getHT(Level::Tight, syst));
        o_htb.push_back(jet.getHT(Level::Bottom, syst));
        o_met.push_back(**Met_pt);
        o_metphi.push_back(**Met_phi);
        o_centrality.push_back(jet.getCentrality(Level::Tight, syst));
    }
}

float ThreeTop::getLeadPt()
{
    if (channel_ != Channel::SS)
        return 0.;
    else if (static_cast<int>(subChannel_) % 2 == 0)
        return getMuon(pt, 0);
    else
        return getElec(pt, 0);
}

void ThreeTop::printStuff()
{
    std::cout << "Event: " << **event << std::endl;
    std::cout << "Met: " << **Met_pt << std::endl;
    std::cout << "HT: " << jet.getHT(Level::Tight, 0) << std::endl;
    std::cout << "njet: " << jet.size(Level::Tight) << std::endl;
    std::cout << "nbjet: " << jet.size(Level::Bottom) << std::endl;
    std::cout << "nlep: " << muon.size(Level::Tight) << " " << elec.size(Level::Tight) << std::endl;
    std::cout << "lepVeto: " << muon.passZVeto() << " " << elec.passZVeto() << std::endl;
    std::cout << std::endl;
}
