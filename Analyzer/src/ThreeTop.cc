#include "analysis_suite/Analyzer/interface/ThreeTop.h"

#include"analysis_suite/Analyzer/interface/logging.h"
#include"analysis_suite/Analyzer/interface/CommonFuncs.h"

enum class Channel {
    SS_Dilepton,
    SS_Multi,
    TightFake_Nonprompt,
    OS_MisId,
    TTZ_CR,
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

    createTree("Signal_Dilepton", Channel::SS_Dilepton);
    createTree("Signal_Multi", Channel::SS_Multi);
    // Charge Mis-id Fake Rate
    if (!isMC_) {
        createTree("TightFake_Nonprompt", Channel::TightFake_Nonprompt);
        createTree("OS_Charge_MisId", Channel::OS_MisId);
    } else {
        rGen.setup(fReader);
    }

    trigEff_leadPt.setup(fOutput, "leadPt", 4, 100, 0, 100);

    rTop.setup(fReader);

    Met_pt.setup(fReader, "MET_pt");
    Met_phi.setup(fReader, "MET_phi");
    if (isMC_) {
        Pileup_nTrueInt.setup(fReader, "Pileup_nTrueInt");
    }

    setupTrigger(Subchannel::MM, {"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                  "HLT_DoubleMu8_Mass8_PFHT300"});
    setupTrigger(Subchannel::ME, {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
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
    tree->Branch("LooseElectron", "ParticleOut", &o_looseElectrons);
    tree->Branch("TightMuon", "LeptonOut", &o_tightMuons);
    tree->Branch("TightElectron", "LeptonOut", &o_tightElectrons);
    tree->Branch("TightLeptons", "ParticleOut", &o_tightLeptons);
    tree->Branch("Jets", "JetOut", &o_jets);
    tree->Branch("BJets", "JetOut", &o_bJets);
    tree->Branch("ResolvedTops", "TopOut", &o_resolvedTop);

    tree->Branch("HT", &o_ht);
    tree->Branch("HT_b", &o_htb);
    tree->Branch("Met", &o_met);
    tree->Branch("Met_phi", &o_metphi);
    tree->Branch("Centrality", &o_centrality);
    tree->Branch("N_bloose", &o_nb_loose);
    tree->Branch("N_btight", &o_nb_tight);
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
    o_nb_loose.clear();
    o_nb_tight.clear();
    LOG_FUNC << "End of clearOutputs";
}

void ThreeTop::ApplyScaleFactors()
{
    LOG_FUNC << "Start of ApplyScaleFactors";
    LOG_EVENT << "weight: " << (*weight);
    (*weight) *= sfMaker.getPileupSF(*Pileup_nTrueInt);
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

void ThreeTop::setSubChannel()
{
    LOG_FUNC << "Start of setSubChannel";
    subChannel_ = Subchannel::None;

    if (nLeps(Level::Tight) == 1 && nLeps(Level::Fake) == 2) {
        if (muon.size(Level::Fake) == 2) subChannel_ = Subchannel::MM;
        else if (elec.size(Level::Fake) == 2) subChannel_ = Subchannel::EE;
        else if (muon.pt(Level::Fake, 0) > elec.pt(Level::Fake, 0)) subChannel_ = Subchannel::ME;
        else subChannel_ = Subchannel::EM;
    } else if (nLeps(Level::Tight) == 2) {
        if (muon.size(Level::Tight) == 2) subChannel_ = Subchannel::MM;
        else if (elec.size(Level::Tight) == 2) subChannel_ = Subchannel::EE;
        else if (muon.pt(Level::Tight, 0) > elec.pt(Level::Tight, 0)) subChannel_ = Subchannel::ME;
        else subChannel_ = Subchannel::EM;
    } else if (nLeps(Level::Tight) == 3) {
        if (muPt(0) > elPt(0) && muPt(1) > elPt(0)) subChannel_ = Subchannel::MM;
        else if (muPt(0) > elPt(0) && elPt(0) > muPt(1)) subChannel_ = Subchannel::ME;
        else if (elPt(0) > muPt(0) && elPt(1) > muPt(0)) subChannel_ = Subchannel::EE;
        else if (elPt(0) > muPt(0) && muPt(0) > elPt(1)) subChannel_ = Subchannel::EM;
    }
    LOG_FUNC << "End of setSubChannel";
}

bool ThreeTop::isSameSign(Level level)
{
    int q_total = 0;
    for (size_t idx : muon.list(level)) {
        q_total += muon.charge(idx);
    }
    for (size_t idx : elec.list(level)) {
        q_total += elec.charge(idx);
    }
    return abs(q_total) == 1 || abs(q_total) == 2;
}



bool ThreeTop::getCutFlow()
{
    LOG_FUNC << "Start of passSelection";
    (*currentChannel_) = Channel::None;
    setSubChannel();

    if (signal_cuts()) {
        (*currentChannel_) = (nLeps(Level::Tight) == 2) ? Channel::SS_Dilepton : Channel::SS_Multi;
    }

    if (nonprompt_cuts()) (*currentChannel_) = Channel::TightFake_Nonprompt;

    if (charge_misid_cuts()) (*currentChannel_) = Channel::OS_MisId;

    if (ttz_CR_cuts()) (*currentChannel_) = Channel::TTZ_CR;

    if (*currentChannel_ == Channel::None) {
        return false;
    }

    LOG_FUNC << "End of passSelection";
    return true;
}

bool ThreeTop::baseline_cuts(CutInfo& cuts)
{
    LOG_FUNC << "Start of baseline_cuts";
    bool passCuts = true;

    passCuts &= cuts.setCut("passPreselection", true);
    passCuts &= cuts.setCut("passMETFilter", passMetFilters());

    if (passCuts) trigEff_leadPt.fill(getLeadPt(), trig_cuts.pass_cut(subChannel_), subChannel_, *weight);
    passCuts &= cuts.setCut("passTrigger", trig_cuts.pass_cut(subChannel_));
    passCuts &= cuts.setCut("passLeadPt", getLeadPt() > 25);

    passCuts &= cuts.setCut("passJetNumber", jet.size(Level::Tight) >= 2);
    passCuts &= cuts.setCut("passBJetNumber", jet.size(Level::Bottom) >= 1);
    passCuts &= cuts.setCut("passMetCut", *Met_pt > 25);
    passCuts &= cuts.setCut("passHTCut", jet.getHT(Level::Tight) > 300);

    LOG_FUNC << "End of baseline_cuts";
    return passCuts;
}

bool ThreeTop::signal_cuts()
{
    LOG_FUNC << "Start of signal_cuts";
    bool passCuts = true;
    CutInfo cuts;

    passCuts = baseline_cuts(cuts);
    passCuts &= cuts.setCut("passZVeto", muon.passZVeto() && elec.passZVeto());
    passCuts &= cuts.setCut("pass2Or3Leptons", nLeps(Level::Tight) == 2 || nLeps(Level::Tight) == 3);
    passCuts &= cuts.setCut("passSameSign;", isSameSign(Level::Tight));

    // Fill Cut flow
    cuts.setCut("pass2TightLeps", nLeps(Level::Tight) == 2);
    fillCutFlow(Channel::SS_Dilepton, cuts);
    cuts.cuts.pop_back();
    cuts.setCut("pass3TightLeps", nLeps(Level::Tight) == 3);
    fillCutFlow(Channel::SS_Multi, cuts);

    LOG_FUNC << "End of signal_cuts";
    return passCuts;
}

bool ThreeTop::ttz_CR_cuts()
{
    LOG_FUNC << "Start of ttz_CR_cuts";
    bool passCuts = true;
    CutInfo cuts;

    passCuts = baseline_cuts(cuts);
    passCuts &= cuts.setCut("failZVeto", !muon.passZVeto() || !elec.passZVeto());
    passCuts &= cuts.setCut("pass2Leptons", nLeps(Level::Tight) == 3);
    passCuts &= cuts.setCut("passSameSign;", isSameSign(Level::Tight));

    // Fill Cut flow
    fillCutFlow(Channel::TTZ_CR, cuts);

    LOG_FUNC << "End of ttz_CR_cuts";
    return passCuts;
}

bool ThreeTop::nonprompt_cuts()
{
    LOG_FUNC << "Start of nonprompt_cuts";
    bool passCuts = true;
    CutInfo cuts;

    passCuts = baseline_cuts(cuts);
    passCuts &= cuts.setCut("pass1TightLeptons", nLeps(Level::Tight) == 1);
    passCuts &= cuts.setCut("pass2FakeLeptons", nLeps(Level::Fake) == 2);
    passCuts &= cuts.setCut("passSameSign;", isSameSign(Level::Fake));

    // Fill Cut flow
    fillCutFlow(Channel::TightFake_Nonprompt, cuts);

    LOG_FUNC << "End of nonprompt_cuts";
    return passCuts;
}

bool ThreeTop::charge_misid_cuts()
{
    LOG_FUNC << "Start of charge_misid_cuts";
    bool passCuts = true;
    CutInfo cuts;

    passCuts &= cuts.setCut("passZVeto", muon.passZVeto() && elec.passZVeto());
    passCuts &= cuts.setCut("pass2Leptons", nLeps(Level::Tight) == 2);
    passCuts &= cuts.setCut("passOppositeSign;", !isSameSign(Level::Tight));

    // Fill Cut flow
    fillCutFlow(Channel::OS_MisId, cuts);

    LOG_FUNC << "End of charge_misid_cuts";
    return passCuts;
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
    fillParticle(elec, Level::Loose, *o_looseElectrons, pass_bitmap);
    fillLepton(muon, Level::Tight, *o_tightMuons, pass_bitmap);
    fillLepton(elec, Level::Tight, *o_tightElectrons, pass_bitmap);
    fillJet(jet, Level::Tight, *o_jets, pass_bitmap);
    fillJet(jet, Level::Bottom, *o_bJets, pass_bitmap);
    fillTop(rTop, Level::Loose, *o_resolvedTop, pass_bitmap);
    fillAllLeptons(muon, elec, *o_tightLeptons, pass_bitmap);

    for (size_t syst = 0; syst < numSystematics(); ++syst) {
        o_ht.push_back(jet.getHT(Level::Tight, syst));
        o_htb.push_back(jet.getHT(Level::Bottom, syst));
        o_met.push_back(*Met_pt);
        o_metphi.push_back(*Met_phi);
        o_centrality.push_back(jet.getCentrality(Level::Tight, syst));
        o_nb_loose.push_back(jet.n_loose_bjet.at(syst));
        o_nb_tight.push_back(jet.n_tight_bjet.at(syst));
    }
    LOG_FUNC << "End of FillValues";
}

float ThreeTop::getLeadPt(size_t idx)
{
    if (subChannel_ == Subchannel::None) {
        return 0.;
    } else if (idx == 0) {
        return (static_cast<int>(subChannel_) % 2 == 0) ? muPt(0) : elPt(0);
    } else if (idx == 1) {
        if (subChannel_ == Subchannel::MM)
            return muPt(0);
        else if (subChannel_ == Subchannel::EM)
            return muPt(1);
        else if (subChannel_ == Subchannel::ME)
            return elPt(0);
        else if (subChannel_ == Subchannel::EE)
            return elPt(1);
    }
    return 0;
}

void ThreeTop::printStuff()
{
    LOG_FUNC << "Start of printStuff";
    std::cout << "Event: " << *event << std::endl;
    std::cout << "Met: " << *Met_pt << std::endl;
    std::cout << "HT: " << jet.getHT(Level::Tight, 0) << std::endl;
    std::cout << "njet: " << jet.size(Level::Tight) << std::endl;
    std::cout << "nbjet: " << jet.size(Level::Bottom) << std::endl;
    std::cout << "nlep: " << muon.size(Level::Tight) << " " << elec.size(Level::Tight) << std::endl;
    std::cout << "nlep loose: " << muon.size(Level::Fake) << " " << elec.size(Level::Fake) << std::endl;
    std::cout << "lepVeto: " << muon.passZVeto() << " " << elec.passZVeto() << std::endl;
    std::cout << std::endl;
    LOG_FUNC << "End of printStuff";
}

