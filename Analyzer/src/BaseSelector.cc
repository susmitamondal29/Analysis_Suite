#include "analysis_suite/Analyzer/interface/BaseSelector.h"

#include"analysis_suite/Analyzer/interface/logging.h"

#include "analysis_suite/Analyzer/interface/Systematic.h"
#include "analysis_suite/Analyzer/interface/ScaleFactors.h"
#include "analysis_suite/Analyzer/interface/CommonFuncs.h"


void BaseSelector::SetupOutTreeBranches(TTree* tree)
{
    tree->Branch("weight", &o_weight);
    tree->Branch("PassEvent", &o_pass_event);
    tree->Branch("run", &o_run);
    tree->Branch("lumiBlock", &o_lumiblock);
    tree->Branch("event", &o_event);
}

void BaseSelector::Init(TTree* tree)
{
    LOG_FUNC << "Start of Init";
    loguru::g_preamble_thread = false;
    loguru::g_preamble_time = false;
    if (!tree)
        return;

    TList* rootSystList = new TList();
    rootSystList->SetName("Systematics");
    rootSystList->Add(new TNamed("Nominal", "Nominal"));
    LOG_POST <<  "Start Reading python inputs";
    for (auto item : *fInput) {
        std::string itemName = item->GetName();
        if (itemName == "MetaData") {
            fOutput->Add(item);
            for (auto data : *static_cast<TList*>(item)) {
                std::string dataName = data->GetName();
                if (dataName == "Year") {
                    std::string year = data->GetTitle();
                    year_ = get_by_val(yearMap, year);
                } else if (dataName == "isData") {
                    isMC_ = static_cast<std::string>(data->GetTitle()) == "False";
                } else if (dataName == "Group") {
                    groupName_ = data->GetTitle();
                }
            }
        } else if (itemName == "Systematics") {
            for (auto systNamed : *static_cast<TList*>(item)) {
                std::string systName = systNamed->GetName();
                systematics_.push_back(syst_by_name.at(systName));
                rootSystList->Add(new TNamed((systName + "_up").c_str(), systName.c_str()));
                rootSystList->Add(new TNamed((systName + "_down").c_str(), systName.c_str()));
            }
        } else if (itemName == "Verbosity") {
            loguru::g_stderr_verbosity = std::stoi(item->GetTitle());
        }
    }
    outdir = outfile->mkdir(groupName_.c_str());
    fOutput->Add(rootSystList);
    LOG_POST << "Finished setting python inputs";
    setupSystematicInfo();
    jetCorrector.setup(year_);

    fReader.SetTree(tree);
    if (isMC_) {
        genWeight.setup(fReader, "genWeight");
    }
    run.setup(fReader, "run");
    lumiblock.setup(fReader, "luminosityBlock");
    event.setup(fReader, "event");


    o_weight.resize(numSystematics());
    o_channels.resize(numSystematics());
    o_pass_event.resize(numSystematics());

    sfMaker.init(isMC_, fReader);
    muon.setup(fReader, isMC_);
    elec.setup(fReader, isMC_);
    jet.setup(fReader, isMC_);
    if (isMC_) {
        rGen.setup(fReader);
        rGenJet.setup(fReader);
    }
    total_events = tree->GetEntries();
    LOG_S(INFO) << "Total number of events: " << total_events;

    LOG_FUNC << "End of Init";
}

Bool_t BaseSelector::Process(Long64_t entry)
{
    if (loguru::g_stderr_verbosity > 5 && entry > 10) return false;
    LOG_FUNC << "Start of Process";
    current_event++;
    if ((current_event % 10000 == 0 || current_event == total_events)
        && loguru::g_stderr_verbosity > 0) {
        LOG_S(INFO) << "At entry " <<  current_event;
        print_bar();
    }

    clearParticles();
    fReader.SetLocalEntry(entry);
    std::vector<bool> systPassSelection;
    bool passAny = false;
    size_t systNum = 0;
    for (auto syst : systematics_) {
        LOG_EVENT_IF(syst != Systematic::Nominal) << "Systematic is " << get_by_val(syst_by_name, syst);

        std::vector<eVar> vars = (syst != Systematic::Nominal) ? syst_vars : nominal_var;
        for (auto var : vars) {
            LOG_EVENT << "Variation is: " << varName_by_var.at(var);
            SetupEvent(syst, var, systNum);
            CutInfo cuts;
            bool passCuts = getCutFlow(cuts);
            bool passTrigger = getTriggerCut(cuts);
            systPassSelection.push_back(passCuts && passTrigger);
            if (syst == Systematic::Nominal) {
                for (auto tree: trees) {
                    tree.fillCutFlow(cuts, *currentChannel_, *weight);
                }
                // fillTriggerEff(passCuts, cuts.back().second);
            }
            passAny |= passCuts && passTrigger;
            systNum++;
        }
    }
    if (systPassSelection[0] && chanInSR(o_channels[0])) {
        passed_events++;
    }

    if (passAny) {
        for (auto tree : trees) {
            bool passedChannel = false;
            for (size_t syst = 0; syst < numSystematics(); ++syst) {
                o_pass_event[syst] = systPassSelection[syst] && tree.contains(o_channels[syst]);
                passedChannel |= o_pass_event[syst];
            }

            if (passedChannel) {
                clearOutputs();
                FillValues(o_pass_event);
                tree.tree->Fill();
            }
        }
    }
    LOG_FUNC << "End of Process";
    return kTRUE;
}

void BaseSelector::SlaveTerminate()
{
    LOG_S(INFO) << passed_events << " events passed selection";
}

void BaseSelector::SetupEvent(Systematic syst, eVar var, size_t systNum)
{
    LOG_FUNC << "Start of SetupEvent";
    SystematicWeights::currentSyst = syst;
    SystematicWeights::currentVar = var;

    weight = &o_weight[systNum];
    currentChannel_ = &o_channels[systNum];

    (*weight) = isMC_ ? *genWeight : 1.0;

    if (isMC_) {
        rGen.createTopList();
    }
    jet.setupJEC(jetCorrector, rGenJet);
    muon.setGoodParticles(systNum, jet, rGen);
    elec.setGoodParticles(systNum, jet, rGen);
    jet.setGoodParticles(systNum);
    setOtherGoodParticles(systNum);
    setupChannel();
    if (isMC_) {
        ApplyScaleFactors();
    }
    LOG_FUNC << "End of SetupEvent";
}

void BaseSelector::clearParticles()
{
    LOG_FUNC << "Start of clearParticles";
    muon.clear();
    elec.clear();
    jet.clear();
    rGen.clear();
    rGenJet.clear();

    std::fill(o_weight.begin(), o_weight.end(), 1.);
    LOG_FUNC << "End of clearParticles";
}

void BaseSelector::setupSystematicInfo()
{
    LOG_FUNC << "Start of setupSystematicInfo";
    std::string scaleDir = getenv("CMSSW_BASE");
    scaleDir += "/src/analysis_suite/data";

    SystematicWeights::nSyst = numSystematics();
    SystematicWeights::year_ = year_;
    SystematicWeights::scaleDir_ = scaleDir;
    SystematicWeights::f_scale_factors = new TFile((scaleDir + "/scale_factors/event_scalefactors.root").c_str());
    LOG_FUNC << "End of setupSystematicInfo";
}


void BaseSelector::FillValues(const std::vector<bool>& passVec) {
    o_run = *run;
    o_lumiblock = *lumiblock;
    o_event = *event;

}

void BaseSelector::print_bar()
{
    // Setup progress bar
    float progress = float(current_event)/total_events;

    std::string bar = "[";
    bar += std::string(int(floor(progress*barWidth)), '=');
    if (bar.size() < barWidth) bar += ">";
    if (bar.size() < barWidth)
        bar += std::string(int((barWidth+1)-bar.size()), ' ');
    bar += "] ";
    bar += std::to_string(progress * 100.0) + " %";
    std::cout << bar << std::endl;

}
