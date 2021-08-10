#include "analysis_suite/Analyzer/interface/ThreeTop.h"

#define getElec(var, i) (elec.var(elec.list(Level::Tight).at(i)))
#define getMuon(var, i) (muon.var(muon.list(Level::Tight).at(i)))

void ThreeTop::Init(TTree* tree)
{
    BaseSelector::Init(tree);
    createTree(groupName_, { Channel::SS, Channel::Multi });

    if (!isMC_) {
        createTree("Nonprompt_FR", { Channel::LooseToTightFake });
    }

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
    if (isMC_) {
        Pileup_nTrueInt = new TTRValue<Float_t>(fReader, "Pileup_nTrueInt");
    }

    //HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8
    HLT_MuMu = new TTRValue<Bool_t>(fReader, "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
    HLT_MuEle = new TTRValue<Bool_t>(fReader, "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL");
    HLT_EleMu = new TTRValue<Bool_t>(fReader, "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL");
    HLT_EleEle = new TTRValue<Bool_t>(fReader, "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL");
}

void ThreeTop::SetupOutTreeBranches(TTree* tree)
{
    BaseSelector::SetupOutTreeBranches(tree);
    tree->Branch("LooseMuon", "ParticleOut", &o_looseMuons);
    tree->Branch("TightMuon", "ParticleOut", &o_tightMuons);
    tree->Branch("LooseElectron", "ParticleOut", &o_looseElectrons);
    tree->Branch("TightElectron", "ParticleOut", &o_tightElectrons);
    tree->Branch("TightLeptons", "ParticleOut", &o_tightLeptons);
    tree->Branch("Jets", "ParticleOut", &o_jets);
    tree->Branch("BJets", "BJetOut", &o_bJets);
    tree->Branch("ResolvedTops", "TopOut", &o_resolvedTop);

    tree->Branch("HT", &o_ht);
    tree->Branch("HT_b", &o_htb);
    tree->Branch("Met", &o_met);
    tree->Branch("Met_phi", &o_metphi);
    tree->Branch("Centrality", &o_centrality);
}

void ThreeTop::clearParticles()
{
    BaseSelector::clearParticles();
    rTop.clear();
    rGen.clear();
}

void ThreeTop::clearOutputs()
{
    o_ht.clear();
    o_htb.clear();
    o_met.clear();
    o_metphi.clear();
    o_centrality.clear();
}

void ThreeTop::ApplyScaleFactors()
{
    (*weight) *= sfMaker.getPileupSF(**Pileup_nTrueInt);
    (*weight) *= sfMaker.getLHESF();

    (*weight) *= jet.getScaleFactor();
    (*weight) *= elec.getScaleFactor();
    (*weight) *= muon.getScaleFactor();
    (*weight) *= rTop.getScaleFactor(rGen);
}

void ThreeTop::setOtherGoodParticles(size_t syst)
{
    rTop.setGoodParticles(syst);
    rGen.setGoodParticles(syst);
}

void ThreeTop::setupChannel()
{
    (*currentChannel_) = Channel::None;
    (subChannel_) = Subchannel::None;
    size_t nLep = muon.size(Level::Tight) + elec.size(Level::Tight);
    size_t nFakeLep = muon.size(Level::Fake) + elec.size(Level::Fake);

    if (nLep == 0) {
        (*currentChannel_) = Channel::Hadronic;
    } else if (nLep == 1 && nFakeLep != 2) {
        (*currentChannel_) = Channel::Single;
    } else {
        /// Channels we care about
        if (nLep == 1 && nFakeLep == 2) {
            muon.moveLevel(Level::Fake, Level::Tight);
            elec.moveLevel(Level::Fake, Level::Tight);
            if (isSameSign()) {
                (*currentChannel_) = Channel::LooseToTightFake;
            } else {
                (*currentChannel_) = Channel::Single;
                return; // don't want to set subchannel (not valid channel)
            }
        } else if (nLep == 2) {
            (*currentChannel_) = (isSameSign()) ? Channel::SS : Channel::OS;
        } else
            (*currentChannel_) = (isSameSign()) ? Channel::Multi : Channel::MultiAllSame;
        setSubChannel();
    }
}

void ThreeTop::setSubChannel()
{
    if (!elec.size(Level::Tight)) {
        subChannel_ = Subchannel::MM;
    } else if (!muon.size(Level::Tight)) {
        subChannel_ = Subchannel::EE;
    } else {
        if (getMuon(pt, 0) > getElec(pt, 0)) {
            if (muon.size(Level::Tight) > 1 && getMuon(pt, 1) > getElec(pt, 0)) {
                subChannel_ = Subchannel::MM;
            } else {
                subChannel_ = Subchannel::ME;
            }
        } else {
            if (elec.size(Level::Tight) > 1 && getElec(pt, 1) > getMuon(pt, 0)) {
                subChannel_ = Subchannel::EE;
            } else {
                subChannel_ = Subchannel::EM;
            }
        }
    }
}

bool ThreeTop::isSameSign()
{
    int q_total = 0;
    for (size_t idx : muon.list(Level::Tight)) {
        q_total += muon.charge(idx);
    }
    for (size_t idx : elec.list(Level::Tight)) {
        q_total += elec.charge(idx);
    }
    return abs(q_total) == 1 || abs(q_total) == 2;
}

bool ThreeTop::passSelection()
{
    std::vector<std::pair<std::string, bool>> cuts;
    cuts.push_back(std::make_pair("passPreselection", true));

    cuts.push_back(std::make_pair("passMETFilter",
        (**Flag_goodVertices && **Flag_globalSuperTightHalo2016Filter && **Flag_HBHENoiseFilter && **Flag_HBHENoiseIsoFilter && **Flag_EcalDeadCellTriggerPrimitiveFilter && **Flag_BadPFMuonFilter && **Flag_ecalBadCalibFilter)));
    cuts.push_back(std::make_pair("passZVeto", muon.passZVeto() && elec.passZVeto()));
    cuts.push_back(std::make_pair("passJetNumber", jet.size(Level::Tight) >= 2));
    cuts.push_back(std::make_pair("passBJetNumber", jet.size(Level::Bottom) >= 1));
    cuts.push_back(std::make_pair("passMetCut", **Met_pt > 25));
    cuts.push_back(std::make_pair("passHTCut", jet.getHT(Level::Tight) > 300));

    // Trigger stuff
    cuts.push_back(std::make_pair("passLeadPtCut", getLeadPt() > 25));
    cuts.push_back(std::make_pair("passSubLeadPtCut", getLeadPt(1) > 15));

    passTrigger = true;
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
    std::vector<std::pair<std::string, bool>> cuts;
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

float ThreeTop::getLeadPt(size_t idx)
{
    if (subChannel_ == Subchannel::None) {
        return 0.;
    } else if (idx == 0) {
        return (static_cast<int>(subChannel_) % 2 == 0) ? getMuon(pt, 0) : getElec(pt, 0);
    } else if (idx == 1) {
        if (subChannel_ == Subchannel::MM)
            return getMuon(pt, 1);
        else if (subChannel_ == Subchannel::EM)
            return getMuon(pt, 0);
        else if (subChannel_ == Subchannel::ME)
            return getElec(pt, 0);
        else if (subChannel_ == Subchannel::EE)
            return getElec(pt, 1);
    }

    return 0;
}

void ThreeTop::printStuff()
{
    std::cout << "Event: " << **event << std::endl;
    std::cout << "Met: " << **Met_pt << std::endl;
    std::cout << "HT: " << jet.getHT(Level::Tight, 0) << std::endl;
    std::cout << "njet: " << jet.size(Level::Tight) << std::endl;
    std::cout << "nbjet: " << jet.size(Level::Bottom) << std::endl;
    std::cout << "nlep: " << muon.size(Level::Tight) << " " << elec.size(Level::Tight) << std::endl;
    std::cout << "nlep loose: " << muon.size(Level::Fake) << " " << elec.size(Level::Fake) << std::endl;
    std::cout << "lepVeto: " << muon.passZVeto() << " " << elec.passZVeto() << std::endl;
    std::cout << std::endl;
}
