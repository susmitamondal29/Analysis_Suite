#include "analysis_suite/skim/interface/ZZto4l.h"

#include"analysis_suite/skim/interface/logging.h"
#include"analysis_suite/skim/interface/CommonFuncs.h"

enum class Channel {
    Signal,
    None,
};

enum class Subchannel {
    EEEE,
    EEMM,
    MMMM,
    None,
};

#define getElec(var, i) (elec.var(elec.list(Level::Tight).at(i)))
#define getMuon(var, i) (muon.var(muon.list(Level::Tight).at(i)))

void ZZto4l::Init(TTree* tree)
{
    LOG_FUNC << "Start of Init";
    BaseSelector::Init(tree);

    createTree("Signal", Channel::Signal);

    // trigEff_leadPt.setup(fOutput, "leadPt", 4, 100, 0, 100);

    zBoson.setup(fReader, &elec);

    if (isMC_) {
        Pileup_nTrueInt.setup(fReader, "Pileup_nTrueInt");
    }

    setupTrigger(Subchannel::None);

    LOG_FUNC << "End of Init";
}

void ZZto4l::SetupOutTreeBranches(TTree* tree)
{
    LOG_FUNC << "Start of SetupOutTreeBranches";
    BaseSelector::SetupOutTreeBranches(tree);
    tree->Branch("Z_To_EE", "ParticleOut", &o_Z_ee);
    tree->Branch("Z_To_MM", "ParticleOut", &o_Z_mm);

    LOG_FUNC << "End of SetupOutTreeBranches";
}

void ZZto4l::clearParticles()
{
    LOG_FUNC << "Start of clearParticles";
    BaseSelector::clearParticles();
    zBoson.clear();
    LOG_FUNC << "End of clearParticles";
}

void ZZto4l::clearOutputs()
{
    LOG_FUNC << "Start of clearOutputs";

    LOG_FUNC << "End of clearOutputs";
}

void ZZto4l::ApplyScaleFactors()
{
    LOG_FUNC << "Start of ApplyScaleFactors";
    // LOG_EVENT << "weight: " << (*weight);
    // (*weight) *= sfMaker.getPileupSF(*Pileup_nTrueInt);
    // LOG_EVENT << "weight after pu scale: " << (*weight);
    // (*weight) *= sfMaker.getLHESF();
    // LOG_EVENT << "weight after lhe scale: " << (*weight);
    // (*weight) *= sfMaker.getLHEPdf();
    // LOG_EVENT << "weight after pdf scale: " << (*weight);
    // (*weight) *= sfMaker.getPartonShower();
    // LOG_EVENT << "weight after ps scale: " << (*weight);
    // (*weight) *= jet.getScaleFactor();
    // LOG_EVENT << "weight after jet scale: " << (*weight);
    // (*weight) *= jet.getTotalBTagWeight();
    // LOG_EVENT << "weight after bjet scale: " << (*weight);
    // (*weight) *= elec.getScaleFactor();
    // LOG_EVENT << "weight after elec scale: " << (*weight);
    // (*weight) *= muon.getScaleFactor();
    // LOG_EVENT << "weight after muon scale: " << (*weight);
    LOG_FUNC << "End of ApplyScaleFactors";
}

void ZZto4l::ApplyDataScaleFactors()
{}

void ZZto4l::setOtherGoodParticles(size_t syst)
{
    LOG_FUNC << "Start of setOtherGoodParticles";
    zBoson.setGoodParticles(syst);
    LOG_FUNC << "End of setOtherGoodParticles";
}

void ZZto4l::setSubChannel()
{
    LOG_FUNC << "Start of setSubChannel";
    subChannel_ = Subchannel::None;
    LOG_FUNC << "End of setSubChannel";
}


bool ZZto4l::getCutFlow()
{
    LOG_FUNC << "Start of passSelection";
    (*currentChannel_) = Channel::None;
    setSubChannel();

    if (signal_cuts()) (*currentChannel_) = Channel::Signal;

    if (trees.find(*currentChannel_) == trees.end()) {
        return false;
    }

    // if (!isMC_)  ApplyDataScaleFactors();

    LOG_FUNC << "End of passSelection";
    return true;
}


bool ZZto4l::signal_cuts()
{
    LOG_FUNC << "Start of signal_cuts";
    bool passCuts = true;
    CutInfo cuts;

    passCuts &= cuts.setCut("passPreselection", true);
    // passCuts &= cuts.setCut("passMETFilter", metfilters.pass());

    // // if (passCuts) trigEff_leadPt.fill(getLeadPt(), trig_cuts.pass_cut(subChannel_), subChannel_, *weight);
    // passCuts &= cuts.setCut("passTrigger", trig_cuts.pass_cut(subChannel_));
    // passCuts &= cuts.setCut("passLeadPt", getLeadPt() > 25);

    // passCuts &= cuts.setCut("passJetNumber", jet.size(Level::Tight) >= 2);
    // passCuts &= cuts.setCut("passBJetNumber", jet.size(Level::Bottom) >= 1);
    // passCuts &= cuts.setCut("passMetCut", met.pt() > 25);
    // passCuts &= cuts.setCut("passHTCut", jet.getHT(Level::Tight) > 250);

    // passCuts &= cuts.setCut("pass2Or3Leptons", nLeps(Level::Tight) == 2 || nLeps(Level::Tight) == 3);
    // passCuts &= cuts.setCut("passSameSign;", isSameSign(Level::Tight));

    // // Fill Cut flow
    // cuts.setCut("pass2TightLeps", nLeps(Level::Tight) == 2);
    // fillCutFlow(Channel::SS_Dilepton, cuts);
    // cuts.cuts.pop_back();
    // cuts.setCut("pass3TightLeps", nLeps(Level::Tight) == 3);
    // fillCutFlow(Channel::SS_Multi, cuts);

    LOG_FUNC << "End of signal_cuts";
    return passCuts;
}


void ZZto4l::FillValues(const std::vector<bool>& passVec)
{
    LOG_FUNC << "Start of FillValues";
    BaseSelector::FillValues(passVec);
    size_t pass_bitmap = 0;
    for (size_t i = 0; i < passVec.size(); ++i) {
        pass_bitmap += passVec.at(i) << i;
    }

    zBoson.fillOutput(*o_Z_ee, Level::EE, pass_bitmap);
    zBoson.fillOutput(*o_Z_mm, Level::MM, pass_bitmap);

    for (size_t syst = 0; syst < numSystematics(); ++syst) {

    }
    LOG_FUNC << "End of FillValues";
}


void ZZto4l::printStuff()
{
    LOG_FUNC << "Start of printStuff";
    std::cout << "Event: " << *event << std::endl;
    std::cout << "Met: " << met.pt() << std::endl;
    std::cout << "HT: " << jet.getHT(Level::Tight, 0) << std::endl;
    std::cout << "njet: " << jet.size(Level::Tight) << std::endl;
    std::cout << "nbjet: " << jet.size(Level::Bottom) << std::endl;
    std::cout << "nlep: " << muon.size(Level::Tight) << " " << elec.size(Level::Tight) << std::endl;
    std::cout << "nlep loose: " << muon.size(Level::Fake) << " " << elec.size(Level::Fake) << std::endl;
    std::cout << "lepVeto: " << muon.passZVeto() << " " << elec.passZVeto() << std::endl;
    std::cout << std::endl;
    LOG_FUNC << "End of printStuff";
}
