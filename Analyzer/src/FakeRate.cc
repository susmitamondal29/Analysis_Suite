#include "analysis_suite/Analyzer/interface/FakeRate.h"

#include "analysis_suite/Analyzer/interface/logging.h"

enum class Channel {
    Measurement,
    SideBand,
    FullMet,
    TightTight,
    TightFake,
    None,
};

enum class Subchannel {
    M,
    E,
    MM,
    EM,
    ME,
    EE,
    None,
};

void FakeRate::Init(TTree* tree)
{
    LOG_FUNC << "Start of Init";
    BaseSelector::Init(tree);

    // Only process for QCD, data, ewk
    if (groupName_.find("qcd") != std::string::npos || !isMC_
        || ewk_sets.find(groupName_) != ewk_sets.end()) {
        createTree("Measurement", Channel::Measurement);
        createTree("SideBand", Channel::SideBand);
    }
    if (groupName_.find("qcd") == std::string::npos) {
        createTree("Closure_TF", Channel::TightFake);
        if (isMC_) {
            createTree("Closure_TT", Channel::TightTight);
        }
    }
    muon.setup_map(Level::FakeNotTight);
    elec.setup_map(Level::FakeNotTight);

    std::string met_name = (year_ == Year::yr2017) ? "METFixEE2017" : "MET";
    Met_pt.setup(fReader, (met_name+"_pt").c_str());
    Met_phi.setup(fReader, (met_name+"_phi").c_str());

    if (isMC_) {
        Pileup_nTrueInt.setup(fReader, "Pileup_nTrueInt");
    }

    sfMaker.setup_prescale();

    // Single Lepton Triggers
    setupTrigger(Subchannel::M, {"HLT_Mu8_TrkIsoVVL",
                                 "HLT_Mu17_TrkIsoVVL"});
    setupTrigger(Subchannel::E, {"HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30",
                                 "HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30"});
    // Dilepton triggers
    if (year_ == Year::yr2016) {
        setupTrigger(Subchannel::MM, {"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"});
        setupTrigger(Subchannel::ME, {"HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
                                      "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                      "HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ",
                                      "HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL"});
        setupTrigger(Subchannel::EM, {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                      "HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL",
                                      "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                      "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL"});
        setupTrigger(Subchannel::EE, {"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"});
    } else if(year_ == Year::yr2017) {
        setupTrigger(Subchannel::MM, {"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8"});
        setupTrigger(Subchannel::ME, {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"});
        setupTrigger(Subchannel::EM, {"HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"});
        setupTrigger(Subchannel::EE, {"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"});
    } else if (year_ == Year::yr2018) {
        setupTrigger(Subchannel::MM, {"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"});
        setupTrigger(Subchannel::ME, {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"});
        setupTrigger(Subchannel::EM, {"HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"});
        setupTrigger(Subchannel::EE, {"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"});
    }

    setupTrigger(Subchannel::None);

    LOG_FUNC << "End of Init";
}

void FakeRate::SetupOutTreeBranches(TTree* tree)
{
    LOG_FUNC << "Start of SetupOutTreeBranches";
    BaseSelector::SetupOutTreeBranches(tree);
    tree->Branch("FakeMuon", "ParticleOut", &o_fakeMuons);
    tree->Branch("TightMuon", "ParticleOut", &o_tightMuons);
    tree->Branch("FakeElectron", "ParticleOut", &o_fakeElectrons);
    tree->Branch("TightElectron", "ParticleOut", &o_tightElectrons);
    tree->Branch("Jets", "JetOut", &o_jets);
    tree->Branch("BJets", "JetOut", &o_bJets);

    tree->Branch("HT", &o_ht);
    tree->Branch("HT_b", &o_htb);
    tree->Branch("Met", &o_met);
    tree->Branch("Met_phi", &o_metphi);
    tree->Branch("N_bloose", &o_nb_loose);
    tree->Branch("N_btight", &o_nb_tight);
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
    o_nb_loose.clear();
    o_nb_tight.clear();
    LOG_FUNC << "End of clearOutputs";
}

void FakeRate::ApplyScaleFactors()
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
    LOG_FUNC << "End of ApplyScaleFactors";
}

void FakeRate::ApplyDataSpecifics()
{
    if (nLeps(Level::Fake) == 1) {
        std::string trig_string;
        if (lead_lep.Pt() < 25) trig_string = trig_cuts.trigger_names[subChannel_].at(0);
        else trig_string = trig_cuts.trigger_names[subChannel_].at(1);
        (*weight) *= sfMaker.getPrescale(*run, *lumiblock, trig_string);
    }
}

void FakeRate::setOtherGoodParticles(size_t syst)
{
    LOG_FUNC << "Start of setOtherGoodParticles";
    muon.xorLevel(Level::Fake, Level::Tight, Level::FakeNotTight);
    elec.xorLevel(Level::Fake, Level::Tight, Level::FakeNotTight);
    LOG_FUNC << "End of setOtherGoodParticles";
}

void FakeRate::setSubChannel()
{
    LOG_FUNC << "Start of setSubChannel";
    subChannel_ = Subchannel::None;

    if (nLeps(Level::Fake) == 1) {
        subChannel_ = muon.size(Level::Fake) == 1 ? Subchannel::M : Subchannel::E;
    } else if (nLeps(Level::Fake) == 2) {
        if (muon.size(Level::Fake) == 2) {
            subChannel_ = Subchannel::MM;
        } else if (elec.size(Level::Fake) == 2) {
            subChannel_ = Subchannel::EE;
        } else if (muon.pt(Level::Fake, 0) > elec.pt(Level::Fake, 0)) {
            subChannel_ = Subchannel::ME;
        } else {
            subChannel_ = Subchannel::EM;
        }
    }
    LOG_FUNC << "End of setSubChannel";
}

bool FakeRate::isSameSign()
{
    int q_total = 0;
    for (size_t idx : muon.list(Level::Fake)) {
        q_total += muon.charge(idx);
    }
    for (size_t idx : elec.list(Level::Fake)) {
        q_total += elec.charge(idx);
    }
    // if 2 leptons, SS -> +1 +1 / -1 -1 -> abs(q) == 2
    // OS cases are 0 and 3, so no overlap
    return abs(q_total) == 1 || abs(q_total) == 2;
}


bool FakeRate::getCutFlow()
{
    LOG_FUNC << "Start of passSelection";
    (*currentChannel_) = Channel::None;
    setSubChannel();
    set_leadlep();

    if (measurement_cuts()) (*currentChannel_) = Channel::Measurement;

    if (sideband_cuts()) (*currentChannel_) = Channel::SideBand;

    if (closure_cuts()) {
        if (nLeps(Level::Tight) == 2) (*currentChannel_) = Channel::TightTight;
        else (*currentChannel_) = Channel::TightFake;
    }

    if (*currentChannel_ == Channel::None) {
        return false;
    }

    if (!isMC_) {
        ApplyDataSpecifics();
    }

    LOG_FUNC << "End of passSelection";
    return true;
}

bool FakeRate::single_lep_cuts(CutInfo& cuts)
{
    bool passCuts = true;
    bool haveOneFake = nLeps(Level::Fake) == 1;

    passCuts &= cuts.setCut("passPreselection", true);
    passCuts &= cuts.setCut("passMETFilter", passMetFilters());
    passCuts &= cuts.setCut("pass1FakeLep", haveOneFake);
    // TriggerCuts
    bool trig_match = false;
    if (haveOneFake) {
        trig_match = (lead_lep.Pt() < 25 && *trig_cuts.trigs[subChannel_].at(0)) || ( lead_lep.Pt() >= 25 && *trig_cuts.trigs[subChannel_].at(1));
    }
    passCuts &= cuts.setCut("passLeadPtCut", trig_match);
    passCuts &= cuts.setCut("passTrigger", trig_cuts.pass_cut(subChannel_));

    bool hasFarJet = false;
    if (haveOneFake) {
        for (auto jidx: jet.list(Level::Tight)) {
            if (deltaR(lead_lep.Eta(), jet.eta(jidx), lead_lep.Phi(), jet.phi(jidx)) > 1) {
                hasFarJet = true;
                break;
            }
        }
    }
    passCuts &= cuts.setCut("passHasFarJet", hasFarJet);

    return passCuts;
}

bool FakeRate::measurement_cuts()
{
    bool passCuts = true;
    CutInfo cuts;

    passCuts &= single_lep_cuts(cuts);
    passCuts &= cuts.setCut("passMetCut", *Met_pt < 30);
    passCuts &= cuts.setCut("passMtCut", mt_f(lead_lep.Pt(), *Met_pt, lead_lep.Phi(), *Met_phi) < 20);

    // Fill Cut flow
    fillCutFlow(Channel::Measurement, cuts);

    return passCuts;
}

bool FakeRate::sideband_cuts()
{
    bool passCuts = true;
    CutInfo cuts;

    passCuts &= single_lep_cuts(cuts);
    passCuts &= cuts.setCut("passMetCut", *Met_pt > 30);
    passCuts &= cuts.setCut("passTightLep", nLeps(Level::Tight) == 1);
    passCuts &= cuts.setCut("passLeadLepPt", lead_lep.Pt() > 20);

    // Fill Cut flow
    fillCutFlow(Channel::SideBand, cuts);

    return passCuts;
}

bool FakeRate::closure_cuts()
{
    bool passCuts = true;
    CutInfo cuts;

    passCuts &= cuts.setCut("passPreselection", true);
    passCuts &= cuts.setCut("passMETFilter", passMetFilters());
    passCuts &= cuts.setCut("pass2FakeLep",  nLeps(Level::Fake) == 2);
    passCuts &= cuts.setCut("passTightLep", nLeps(Level::Tight) >= 1);
    // Trigger Cuts
    passCuts &= cuts.setCut("passLeadPtCut", getLeadPt() > 25);
    passCuts &= cuts.setCut("passTrigger", trig_cuts.pass_cut(subChannel_));

    passCuts &= cuts.setCut("passSSLeptons", isSameSign());
    passCuts &= cuts.setCut("passZVeto", muon.passZVeto() && elec.passZVeto());
    passCuts &= cuts.setCut("passJetNumber", jet.size(Level::Tight) >= 2);
    passCuts &= cuts.setCut("passMetCut", *Met_pt > 50);
    passCuts &= cuts.setCut("passHTCut", jet.getHT(Level::Tight) > 100);

    // Fill Cut flow
    cuts.setCut("pass2TightLeps", nLeps(Level::Tight) == 2);
    fillCutFlow(Channel::TightTight, cuts);
    cuts.cuts.pop_back();
    cuts.setCut("pass1TightLeps", nLeps(Level::Tight) == 1);
    fillCutFlow(Channel::TightFake, cuts);

    return passCuts;
}

void FakeRate::set_leadlep()
{
    if (nLeps(Level::Fake) != 1) {
        return;
    } else if (muon.size(Level::Fake) == 1) {
        lead_lep = muon.p4(Level::Fake, 0);
    } else {
        lead_lep = elec.p4(Level::Fake, 0);
    }
}

float FakeRate::getLeadPt()
{
    if (subChannel_ == Subchannel::MM || subChannel_ == Subchannel::ME) {
        return muon.pt(Level::Fake, 0);
    } else if (subChannel_ == Subchannel::EE || subChannel_ == Subchannel::EM) {
        return elec.pt(Level::Fake, 0);
    }
    return 0.;
}

void FakeRate::FillValues(const std::vector<bool>& passVec)
{
    LOG_FUNC << "Start of FillValues";
    BaseSelector::FillValues(passVec);
    size_t pass_bitmap = 0;
    for (size_t i = 0; i < passVec.size(); ++i) {
        pass_bitmap += passVec.at(i) << i;
    }

    fillParticle(muon, Level::FakeNotTight, *o_fakeMuons, pass_bitmap);
    fillParticle(muon, Level::Tight, *o_tightMuons, pass_bitmap);
    fillParticle(elec, Level::FakeNotTight, *o_fakeElectrons, pass_bitmap);
    fillParticle(elec, Level::Tight, *o_tightElectrons, pass_bitmap);
    fillJet(jet, Level::Tight, *o_jets, pass_bitmap);
    fillJet(jet, Level::Bottom, *o_bJets, pass_bitmap);

    for (size_t syst = 0; syst < numSystematics(); ++syst) {
        o_ht.push_back(jet.getHT(Level::Tight, syst));
        o_htb.push_back(jet.getHT(Level::Bottom, syst));
        o_met.push_back(*Met_pt);
        o_metphi.push_back(*Met_phi);
        o_nb_loose.push_back(jet.n_loose_bjet.at(syst));
        o_nb_tight.push_back(jet.n_tight_bjet.at(syst));
    }
    LOG_FUNC << "End of FillValues";
}
