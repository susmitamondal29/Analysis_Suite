#include "analysis_suite/Analyzer/interface/BaseSelector.h"

#include "analysis_suite/Analyzer/interface/Systematic.h"
#include "analysis_suite/Analyzer/interface/ScaleFactors.h"

size_t BaseSelector::numSystematics()
{
    size_t total = 0;
    for (auto syst : systematics_) {
        total += var_by_syst.at(syst).size();
    }
    return total;
};

void BaseSelector::SetupOutTreeBranches(TTree* tree)
{
    tree->Branch("weight", &o_weight);
    tree->Branch("PassEvent", &o_pass_event);
}

void BaseSelector::Init(TTree* tree)
{
    if (!tree)
        return;

    TList* rootSystList = new TList();
    rootSystList->SetName("Systematics");
    rootSystList->Add(new TNamed("Nominal", "Nominal"));

    for (auto item : *fInput) {
        std::string itemName = item->GetName();
        if (itemName == "MetaData") {
            fOutput->Add(item);
            for (auto data : *static_cast<TList*>(item)) {
                std::string dataName = data->GetName();
                if (dataName == "Year") {
                    year_ = yearMap.at(data->GetTitle());
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
        }
    }
    fOutput->Add(rootSystList);

    setupSystematicInfo();

    fReader.SetTree(tree);
    if (isMC_) {
        genWeight = new TTreeReaderValue<Float_t>(fReader, "genWeight");
    }

    o_weight.resize(numSystematics());
    o_channels.resize(numSystematics());
    o_pass_event.resize(numSystematics());

    sfMaker.init(isMC_, fReader);

    muon.setup(fReader);
    elec.setup(fReader);
    jet.setup(fReader, isMC_);
}

Bool_t BaseSelector::Process(Long64_t entry)
{
    if (entry % 10000 == 0)
        std::cout << "At entry: " << entry << std::endl;

    clearParticles();
    fReader.SetLocalEntry(entry);
    std::vector<bool> systPassSelection;
    bool passAny = false;
    size_t systNum = 0;
    for (auto syst : systematics_) {
        for (auto var : var_by_syst.at(syst)) {
            SetupEvent(syst, var, systNum);
            systPassSelection.push_back(passSelection());
            // if (syst == Systematic::Nominal) {
            //     fillCutFlow();
            // }
            passAny |= systPassSelection.back();
            systNum++;
        }
    }
    if (systPassSelection[0] && trees.at(0).contains(o_channels[0])) {
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

    return kTRUE;
}

void BaseSelector::SlaveTerminate()
{
    std::cout << passed_events << " events passed selection" << std::endl;
}

void BaseSelector::SetupEvent(Systematic syst, Variation var, size_t systNum)
{
    weight = &o_weight[systNum];
    currentChannel_ = &o_channels[systNum];

    (*weight) = isMC_ ? **genWeight : 1.0;

    muon.setGoodParticles(systNum, jet);
    elec.setGoodParticles(systNum, jet);
    jet.setGoodParticles(systNum);
    setOtherGoodParticles(systNum);

    SystematicWeights::currentSyst = syst;
    SystematicWeights::currentVar = var;

    setupChannel();

    if (isMC_) {
        ApplyScaleFactors();
    }
}

void BaseSelector::clearParticles()
{
    muon.clear();
    elec.clear();
    jet.clear();

    std::fill(o_weight.begin(), o_weight.end(), 1.);
}

void BaseSelector::setupSystematicInfo()
{
    std::string scaleDir = getenv("CMSSW_BASE");
    scaleDir += "/src/analysis_suite/data/scale_factors/";

    SystematicWeights::nSyst = numSystematics();
    SystematicWeights::year_ = year_;
    SystematicWeights::scaleDir_ = scaleDir;
    SystematicWeights::f_scale_factors = new TFile((scaleDir + "event_scalefactors.root").c_str());
    if (year_ == Year::yr2016) {
        SystematicWeights::yearStr_ = "2016";
    } else if (year_ == Year::yr2017) {
        SystematicWeights::yearStr_ = "2017";
    } else {
        SystematicWeights::yearStr_ = "2018";
    }
}
