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

    setupTrigger(Subchannel::M, {"HLT_Mu8",
                                 "HLT_Mu17"});
    setupTrigger(Subchannel::E, {"HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30",
                                 "HLT_Ele17_CaloIdL_TrackIdL_IsoVL"});

    // setupTrigger(Subchannel::EE, {"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
    //                               "HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT300"});
    setupTrigger(Subchannel::None);

    LOG_FUNC << "End of Init";
}

void FakeRate::SetupOutTreeBranches(TTree* tree)
{
    LOG_FUNC << "Start of SetupOutTreeBranches";
    BaseSelector::SetupOutTreeBranches(tree);
    tree->Branch("LooseMuon", "LeptonOut", &o_looseMuons);
    tree->Branch("TightMuon", "LeptonOut", &o_tightMuons);
    tree->Branch("LooseElectron", "LeptonOut", &o_looseElectrons);
    tree->Branch("TightElectron", "LeptonOut", &o_tightElectrons);
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
        float mt = mt_f(lepton.fakePt(Level::Fake, 0, jet), *Met_pt, lepton.phi(Level::Fake, 0), *Met_phi);
        size_t close_jet = lepton.closeJet_by_lepton[lepton.idx(Level::Fake, 0)];
        if (*Met_pt < 20 && mt < 20) {
            (*currentChannel_) = Channel::NP_FR;
        } else if (*Met_pt > 30 && lepton.pt(0) > 20) {
            (*currentChannel_) = Channel::NP_FullMt;
        }

    }
    LOG_FUNC << "End of setupChannel";
}

void FakeRate::setSubChannel()
{
    LOG_FUNC << "Start of setSubChannel";


}

bool FakeRate::getCutFlow(cut_info& cuts)
{
    LOG_FUNC << "Start of passSelection";
    bool passCuts = true;
    passCuts &= setCut(cuts, "passPreselection", true);
    size_t nFakeLep = muon.size(Level::Fake) + elec.size(Level::Fake);
    passCuts &= setCut(cuts, "passFakeLep", nFakeLep == 1);
    bool haveFarJet = false;
    if (nFakeLep == 1) {
        Lepton lepton = (subChannel_ == Subchannel::M) ? static_cast<Lepton>(muon) : static_cast<Lepton>(elec);
        float lphi = lepton.phi(Level::Fake, 0);
        float leta = lepton.eta(Level::Fake, 0);
        for (auto jidx: jet.list(Level::Loose)) {
            float jphi = jet.phi(jidx);
            float jeta = jet.eta(jidx);
            float dr = pow((lphi-jphi), 2) + pow((leta-jeta), 2);
            if (dr > 1) {
                haveFarJet = true;
                break;
            }
        }
    }
    passCuts &= setCut(cuts, "passHasFarJet", haveFarJet);
    // passCuts &= setCut(cuts, "passMETFilter", (*Flag_goodVertices && *Flag_globalSuperTightHalo2016Filter && *Flag_HBHENoiseFilter && *Flag_HBHENoiseIsoFilter && *Flag_EcalDeadCellTriggerPrimitiveFilter && *Flag_BadPFMuonFilter && *Flag_ecalBadCalibFilter));
    // if (muon.passZVeto() && elec.passZVeto()) {
    //     passCuts &= setCut(cuts, "passZVeto", true);
    // } else if (chanInSR(*currentChannel_)) {
    //     passCuts &= setCut(cuts, "failZVeto", true);
    //     (*currentChannel_) = Channel::CR_Z;
    // }
    // passCuts &= setCut(cuts, "passJetNumber", jet.size(Level::Tight) >= 2);
    // passCuts &= setCut(cuts, "passBJetNumber", jet.size(Level::Bottom) >= 1);
    // passCuts &= setCut(cuts, "passMetCut", *Met_pt > 25);
    // passCuts &= setCut(cuts, "passHTCut", jet.getHT(Level::Tight) > 300);

    LOG_FUNC << "End of passSelection";
    return passCuts;
}

bool FakeRate::getTriggerCut(cut_info& cuts) {
    bool passTriggerCuts = true;
    // passTriggerCuts &= setCut(cuts, "passLeadPtCut", getLeadPt() > 25);
    // passTriggerCuts &= setCut(cuts, "passSubLeadPtCut", getLeadPt(1) > 20);
    return BaseSelector::getTriggerCut(cuts);
}

void FakeRate::FillValues(const std::vector<bool>& passVec)
{
    LOG_FUNC << "Start of FillValues";
    BaseSelector::FillValues(passVec);
    size_t pass_bitmap = 0;
    for (size_t i = 0; i < passVec.size(); ++i) {
        pass_bitmap += passVec.at(i) << i;
    }

    fillLepton(muon, Level::Fake, *o_looseMuons, pass_bitmap, *Met_pt, *Met_phi);
    fillLepton(muon, Level::Tight, *o_tightMuons, pass_bitmap, *Met_pt, *Met_phi);
    fillLepton(elec, Level::Fake, *o_looseElectrons, pass_bitmap, *Met_pt, *Met_phi);
    fillLepton(elec, Level::Tight, *o_tightElectrons, pass_bitmap, *Met_pt, *Met_phi);
    fillJet(jet, Level::Tight, *o_jets, pass_bitmap);
    fillBJet(jet, Level::Bottom, *o_bJets, pass_bitmap);

    for (size_t syst = 0; syst < numSystematics(); ++syst) {
        o_ht.push_back(jet.getHT(Level::Tight, syst));
        o_htb.push_back(jet.getHT(Level::Bottom, syst));
        o_met.push_back(*Met_pt);
        o_metphi.push_back(*Met_phi);
        Lepton lepton = (subChannel_ == Subchannel::M) ? static_cast<Lepton>(muon) : static_cast<Lepton>(elec);
        o_mt.push_back(lepton.getMT(Level::Fake, 0, *Met_pt, *Met_phi));
    }
    LOG_FUNC << "End of FillValues";
}
