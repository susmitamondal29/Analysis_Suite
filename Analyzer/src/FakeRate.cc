#include "analysis_suite/Analyzer/interface/FakeRate.h"

#include "analysis_suite/Analyzer/interface/logging.h"

enum class Channel {
    NP_FR,
    NP_FullMt,
    NP_ZCR,
    None,
};

enum class Subchannel {
    M,
    E,
    None,
};

void FakeRate::Init(TTree* tree)
{
    LOG_FUNC << "Start of Init";
    BaseSelector::Init(tree);
    createTree("Nonprompt_FR", { Channel::NP_FR });
    createTree("Nonprompt_FullMt", { Channel::NP_FullMt });
    // createTree("Nonprompt_ZCR", { Channel::NP_ZCR});

    Flag_goodVertices.setup(fReader, "Flag_goodVertices");
    Flag_globalSuperTightHalo2016Filter.setup(fReader, "Flag_globalSuperTightHalo2016Filter");
    Flag_HBHENoiseFilter.setup(fReader, "Flag_HBHENoiseFilter");
    Flag_HBHENoiseIsoFilter.setup(fReader, "Flag_HBHENoiseIsoFilter");
    Flag_EcalDeadCellTriggerPrimitiveFilter.setup(fReader, "Flag_EcalDeadCellTriggerPrimitiveFilter");
    Flag_BadPFMuonFilter.setup(fReader, "Flag_BadPFMuonFilter");
    Flag_ecalBadCalibFilter.setup(fReader, "Flag_ecalBadCalibFilter");
    Met_pt.setup(fReader, "MET_pt");
    Met_phi.setup(fReader, "MET_phi");
    if (isMC_) {
        Pileup_nTrueInt.setup(fReader, "Pileup_nTrueInt");
    }

    setupTrigger(Subchannel::M, {// "HLT_Mu8",
            "HLT_Mu8_TrkIsoVVL",
                                 // "HLT_Mu17",
            "HLT_Mu17_TrkIsoVVL"});
    trig_cuts.add_l1seeds({"HLT_Mu8", "HLT_Mu8_TrkIsoVVL"}, "L1_SingleMu7");
    trig_cuts.add_l1seeds({"HLT_Mu17", "HLT_Mu17_TrkIsoVVL"}, "L1_SingleMu10_LowQ");

    setupTrigger(Subchannel::E, {"HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30",
                                 "HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30"});
    trig_cuts.add_l1seed("HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30", "L1_SingleEG10");
    trig_cuts.add_l1seed("HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30" , "L1_SingleEG15");
    setupTrigger(Subchannel::None);

    LOG_FUNC << "End of Init";
}

void FakeRate::SetupOutTreeBranches(TTree* tree)
{
    LOG_FUNC << "Start of SetupOutTreeBranches";
    BaseSelector::SetupOutTreeBranches(tree);
    tree->Branch("LooseMuon", "ParticleOut", &o_looseMuons);
    tree->Branch("TightMuon", "ParticleOut", &o_tightMuons);
    tree->Branch("LooseElectron", "ParticleOut", &o_looseElectrons);
    tree->Branch("TightElectron", "ParticleOut", &o_tightElectrons);
    tree->Branch("Jets", "JetOut", &o_jets);
    tree->Branch("BJets", "BJetOut", &o_bJets);

    tree->Branch("HT", &o_ht);
    tree->Branch("HT_b", &o_htb);
    tree->Branch("Met", &o_met);
    tree->Branch("Met_phi", &o_metphi);
    LOG_FUNC << "End of SetupOutTreeBranches";
}

void FakeRate::clearParticles()
{
    LOG_FUNC << "Start of clearParticles";
    BaseSelector::clearParticles();
    LOG_FUNC << "End of clearParticles";
}

void FakeRate::clearOutputs()
{
    LOG_FUNC << "Start of clearOutputs";
    o_ht.clear();
    o_htb.clear();
    o_met.clear();
    o_metphi.clear();
    LOG_FUNC << "End of clearOutputs";
}

void FakeRate::ApplyScaleFactors()
{
    LOG_FUNC << "Start of ApplyScaleFactors";
    LOG_EVENT << "weight: " << (*weight);
    (*weight) *= sfMaker.getPileupSF(*Pileup_nTrueInt);
    LOG_EVENT << "weight after pu scale: " << (*weight);
    // (*weight) *= sfMaker.getLHESF();
    // LOG_EVENT << "weight after lhe scale: " << (*weight);
    (*weight) *= jet.getScaleFactor();
    LOG_EVENT << "weight after jet scale: " << (*weight);
    (*weight) *= elec.getScaleFactor();
    LOG_EVENT << "weight after elec scale: " << (*weight);
    (*weight) *= muon.getScaleFactor();
    LOG_EVENT << "weight after muon scale: " << (*weight);
    // (*weight) *= rTop.getScaleFactor(rGen);
    LOG_FUNC << "End of ApplyScaleFactors";
}

void FakeRate::setOtherGoodParticles(size_t syst)
{
    LOG_FUNC << "Start of setOtherGoodParticles";
    LOG_FUNC << "End of setOtherGoodParticles";
}

void FakeRate::setupChannel()
{
    LOG_FUNC << "Start of setupChannel";
    (*currentChannel_) = Channel::None;
    (subChannel_) = Subchannel::None;
    size_t nLep = muon.size(Level::Tight) + elec.size(Level::Tight);
    size_t nFakeLep = muon.size(Level::Fake) + elec.size(Level::Fake);

    if (nFakeLep == 1) {
        subChannel_ = muon.size(Level::Fake) ? Subchannel::M : Subchannel::E;
        Lepton lepton = (subChannel_ == Subchannel::M) ? static_cast<Lepton>(muon) : static_cast<Lepton>(elec);
        lead_lep = lepton.p4(lepton.idx(Level::Fake, 0));
        float mt = lepton.getMT(Level::Fake, 0, *Met_pt, *Met_phi);
        if (*Met_pt < 20 && mt < 20) {
            (*currentChannel_) = Channel::NP_FR;
        } else if (nLep == 1 && *Met_pt > 30 && lead_lep.Pt() > 20) {
            (*currentChannel_) = Channel::NP_FullMt;
        }
    }
    LOG_FUNC << "End of setupChannel";
}

void FakeRate::setSubChannel()
{
    LOG_FUNC << "Start of setSubChannel";


}

bool FakeRate::getCutFlow(CutInfo& cuts)
{
    LOG_FUNC << "Start of passSelection";
    bool passCuts = true;
    passCuts &= cuts.setCut("passPreselection", true);
    passCuts &= cuts.setCut("passMETFilter", (*Flag_goodVertices && *Flag_globalSuperTightHalo2016Filter && *Flag_HBHENoiseFilter && *Flag_HBHENoiseIsoFilter && *Flag_EcalDeadCellTriggerPrimitiveFilter && *Flag_BadPFMuonFilter && *Flag_ecalBadCalibFilter));
    size_t nFakeLep = muon.size(Level::Fake) + elec.size(Level::Fake);
    passCuts &= cuts.setCut("passFakeLep", nFakeLep == 1);
    bool haveFarJet = false;
    if (nFakeLep == 1) {
        for (auto jidx: jet.list(Level::Tight)) {
            float dr = deltaR(lead_lep.Eta(), jet.eta(jidx), lead_lep.Phi(), jet.phi(jidx));
            if (dr > 1) {
                haveFarJet = true;
                break;
            }
        }
    }

    passCuts &= cuts.setCut("passHasFarJet", haveFarJet);

    LOG_FUNC << "End of passSelection";
    return passCuts;
}

bool FakeRate::getTriggerCut(CutInfo& cuts) {
    bool passTriggerCuts = true;
    passTriggerCuts &= cuts.setCut("passTrigger", trig_cuts.pass_cut(subChannel_));
    if ((*currentChannel_) != Channel::None && lead_lep.Pt() > 10 && lead_lep.Pt() < 25) {
        if (subChannel_ == Subchannel::M) {
            passTriggerCuts &= cuts.setCut("passTriggerPt", trig_cuts.pass_ind_cut(Subchannel::M,"HLT_Mu8_TrkIsoVVL"));
        } else if (subChannel_ == Subchannel::E) {
            passTriggerCuts &= cuts.setCut("passTriggerPt", trig_cuts.pass_ind_cut(Subchannel::E, "HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30"));
        }
    } else if ((*currentChannel_) != Channel::None && lead_lep.Pt() > 25) {
        if (subChannel_ == Subchannel::M) {
            passTriggerCuts &= cuts.setCut("passTriggerPt", trig_cuts.pass_ind_cut(Subchannel::M,"HLT_Mu17_TrkIsoVVL"));
        } else if (subChannel_ == Subchannel::E) {
            passTriggerCuts &= cuts.setCut("passTriggerPt", trig_cuts.pass_ind_cut(Subchannel::E, "HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30"));
        }
    }
    return passTriggerCuts;
}

void FakeRate::FillValues(const std::vector<bool>& passVec)
{
    LOG_FUNC << "Start of FillValues";
    BaseSelector::FillValues(passVec);
    size_t pass_bitmap = 0;
    for (size_t i = 0; i < passVec.size(); ++i) {
        pass_bitmap += passVec.at(i) << i;
    }

    fillParticle(muon, Level::Fake, *o_looseMuons, pass_bitmap);
    fillParticle(muon, Level::Tight, *o_tightMuons, pass_bitmap);
    fillParticle(elec, Level::Fake, *o_looseElectrons, pass_bitmap);
    fillParticle(elec, Level::Tight, *o_tightElectrons, pass_bitmap);
    fillJet(jet, Level::Tight, *o_jets, pass_bitmap);
    fillBJet(jet, Level::Bottom, *o_bJets, pass_bitmap);

    for (size_t syst = 0; syst < numSystematics(); ++syst) {
        o_ht.push_back(jet.getHT(Level::Tight, syst));
        o_htb.push_back(jet.getHT(Level::Bottom, syst));
        o_met.push_back(*Met_pt);
        o_metphi.push_back(*Met_phi);
    }
    LOG_FUNC << "End of FillValues";
}
