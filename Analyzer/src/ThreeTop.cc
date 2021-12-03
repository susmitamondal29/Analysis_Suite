#include "analysis_suite/Analyzer/interface/ThreeTop.h"

#include"analysis_suite/Analyzer/interface/logging.h"

enum class Channel {
    Hadronic,
    Single,
    LooseToTightFake,
    OS,
    SS,
    Multi,
    MultiAllSame,
    CR_Z,
    None,
};

enum class Subchannel {
    MM,
    EM,
    ME,
    EE,
    None,
};

#define getElec(var, i) (elec.var(elec.list(Level::Tight).at(i)))
#define getMuon(var, i) (muon.var(muon.list(Level::Tight).at(i)))

void ThreeTop::Init(TTree* tree)
{
    LOG_FUNC << "Start of Init";
    BaseSelector::Init(tree);
    createTree("Analyzed", { Channel::SS, Channel::Multi });
    createTree("CR_TTZ", {Channel::CR_Z});

    if (!isMC_) {
        createTree("Nonprompt_FR", { Channel::LooseToTightFake });
    }

    createObject(passTrigger_leadPt, "passTrigger", 4, 0, 4, 100, 0, 100);
    createObject(failTrigger_leadPt, "failTrigger", 4, 0, 4, 100, 0, 100);

    rTop.setup(fReader);

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

    setupTrigger(Subchannel::MM, {"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                  "HLT_DoubleMu8_Mass8_PFHT300"});
    setupTrigger(Subchannel::ME, {"HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL",
                                  "HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT300"});
    setupTrigger(Subchannel::EM, {"HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
                                  "HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT300"});
    setupTrigger(Subchannel::EE, {"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
                                  "HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT300"});
    setupTrigger(Subchannel::None);

    LOG_FUNC << "End of Init";
}

void ThreeTop::SetupOutTreeBranches(TTree* tree)
{
    LOG_FUNC << "Start of SetupOutTreeBranches";
    BaseSelector::SetupOutTreeBranches(tree);
    tree->Branch("LooseMuon", "ParticleOut", &o_looseMuons);
    tree->Branch("TightMuon", "ParticleOut", &o_tightMuons);
    tree->Branch("LooseElectron", "ParticleOut", &o_looseElectrons);
    tree->Branch("TightElectron", "ParticleOut", &o_tightElectrons);
    tree->Branch("TightLeptons", "ParticleOut", &o_tightLeptons);
    tree->Branch("Jets", "JetOut", &o_jets);
    tree->Branch("BJets", "BJetOut", &o_bJets);
    tree->Branch("ResolvedTops", "TopOut", &o_resolvedTop);

    tree->Branch("HT", &o_ht);
    tree->Branch("HT_b", &o_htb);
    tree->Branch("Met", &o_met);
    tree->Branch("Met_phi", &o_metphi);
    tree->Branch("Centrality", &o_centrality);
    LOG_FUNC << "End of SetupOutTreeBranches";
}

void ThreeTop::clearParticles()
{
    LOG_FUNC << "Start of clearParticles";
    BaseSelector::clearParticles();
    rTop.clear();
    LOG_FUNC << "End of clearParticles";
}

void ThreeTop::clearOutputs()
{
    LOG_FUNC << "Start of clearOutputs";
    o_ht.clear();
    o_htb.clear();
    o_met.clear();
    o_metphi.clear();
    o_centrality.clear();
    LOG_FUNC << "End of clearOutputs";
}

void ThreeTop::ApplyScaleFactors()
{
    LOG_FUNC << "Start of ApplyScaleFactors";
    LOG_EVENT << "weight: " << (*weight);
    (*weight) *= sfMaker.getPileupSF(**Pileup_nTrueInt);
    LOG_EVENT << "weight after pu scale: " << (*weight);
    (*weight) *= sfMaker.getLHESF();
    LOG_EVENT << "weight after lhe scale: " << (*weight);
    (*weight) *= jet.getScaleFactor();
    LOG_EVENT << "weight after jet scale: " << (*weight);
    (*weight) *= elec.getScaleFactor();
    LOG_EVENT << "weight after elec scale: " << (*weight);
    (*weight) *= muon.getScaleFactor();
    LOG_EVENT << "weight after muon scale: " << (*weight);
    // (*weight) *= rTop.getScaleFactor(rGen);
    LOG_FUNC << "End of ApplyScaleFactors";
}

void ThreeTop::setOtherGoodParticles(size_t syst)
{
    LOG_FUNC << "Start of setOtherGoodParticles";
    rTop.setGoodParticles(syst);
    LOG_FUNC << "End of setOtherGoodParticles";
}

void ThreeTop::setupChannel()
{
    LOG_FUNC << "Start of setupChannel";
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
        } else if (nLep == 3) {
            (*currentChannel_) = (isSameSign()) ? Channel::Multi : Channel::MultiAllSame;
        } else {
            (*currentChannel_) = Channel::None;
            return;
        }

        setSubChannel();
    }
    LOG_FUNC << "End of setupChannel";
}

void ThreeTop::setSubChannel()
{
    LOG_FUNC << "Start of setSubChannel";
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
    LOG_FUNC << "End of setSubChannel";
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



bool ThreeTop::getCutFlow(cut_info& cuts)
{
     LOG_FUNC << "Start of passSelection";
     bool passCuts = true;
     passCuts &= setCut(cuts, "passPreselection", true);
     passCuts &= setCut(cuts, "passMETFilter", (**Flag_goodVertices && **Flag_globalSuperTightHalo2016Filter && **Flag_HBHENoiseFilter && **Flag_HBHENoiseIsoFilter && **Flag_EcalDeadCellTriggerPrimitiveFilter && **Flag_BadPFMuonFilter && **Flag_ecalBadCalibFilter));
     if (muon.passZVeto() && elec.passZVeto()) {
         passCuts &= setCut(cuts, "passZVeto", true);
     } else if (chanInSR(*currentChannel_)) {
         passCuts &= setCut(cuts, "failZVeto", true);
         (*currentChannel_) = Channel::CR_Z;
     }
     passCuts &= setCut(cuts, "passJetNumber", jet.size(Level::Tight) >= 2);
     passCuts &= setCut(cuts, "passBJetNumber", jet.size(Level::Bottom) >= 1);
     passCuts &= setCut(cuts, "passMetCut", **Met_pt > 25);
     passCuts &= setCut(cuts, "passHTCut", jet.getHT(Level::Tight) > 300);

     LOG_FUNC << "End of passSelection";
     return passCuts;
}

bool ThreeTop::getTriggerCut(cut_info& cuts) {
    bool passTriggerCuts = true;
    passTriggerCuts &= setCut(cuts, "passLeadPtCut", getLeadPt() > 25);
    passTriggerCuts &= setCut(cuts, "passSubLeadPtCut", getLeadPt(1) > 20);
    passTriggerCuts &= BaseSelector::getTriggerCut(cuts); // apply trigger

    return passTriggerCuts;
}

void ThreeTop::fillTriggerEff(bool passCuts, bool passTrigger) {
    if (passCuts && passTrigger) {
        passTrigger_leadPt->Fill(static_cast<int>(subChannel_), getLeadPt(), *weight);
    } else if (passCuts) {
        failTrigger_leadPt->Fill(static_cast<int>(subChannel_), getLeadPt(), *weight);
    }
}

void ThreeTop::FillValues(const std::vector<bool>& passVec)
{
    LOG_FUNC << "Start of FillValues";
    BaseSelector::FillValues(passVec);
    size_t pass_bitmap = 0;
    for (size_t i = 0; i < passVec.size(); ++i) {
        pass_bitmap += passVec.at(i) << i;
    }

    fillParticle(muon, Level::Loose, *o_looseMuons, pass_bitmap);
    fillParticle(muon, Level::Tight, *o_tightMuons, pass_bitmap);
    fillParticle(elec, Level::Loose, *o_looseElectrons, pass_bitmap);
    fillParticle(elec, Level::Tight, *o_tightElectrons, pass_bitmap);
    fillJet(jet, Level::Tight, *o_jets, pass_bitmap);
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
    LOG_FUNC << "End of FillValues";
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
    LOG_FUNC << "Start of printStuff";
    std::cout << "Event: " << **event << std::endl;
    std::cout << "Met: " << **Met_pt << std::endl;
    std::cout << "HT: " << jet.getHT(Level::Tight, 0) << std::endl;
    std::cout << "njet: " << jet.size(Level::Tight) << std::endl;
    std::cout << "nbjet: " << jet.size(Level::Bottom) << std::endl;
    std::cout << "nlep: " << muon.size(Level::Tight) << " " << elec.size(Level::Tight) << std::endl;
    std::cout << "nlep loose: " << muon.size(Level::Fake) << " " << elec.size(Level::Fake) << std::endl;
    std::cout << "lepVeto: " << muon.passZVeto() << " " << elec.passZVeto() << std::endl;
    std::cout << std::endl;
    LOG_FUNC << "End of printStuff";
}
