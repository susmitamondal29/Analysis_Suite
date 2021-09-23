#include "analysis_suite/Analyzer/interface/BaseSelector.h"

#include "analysis_suite/Analyzer/interface/Systematic.h"
#include "analysis_suite/Analyzer/interface/ScaleFactors.h"

size_t BaseSelector::numSystematics()
{
    return systematics_.size()*2 - 1; // up/down for each, but nominal only 1
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
    jetCorrector.setup(year_);

    fReader.SetTree(tree);
    rho = new TTreeReaderValue<Float_t>(fReader, "fixedGridRhoFastjetAll");
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
    if (isMC_) {
        rGen.setup(fReader);
        rGenJet.setup(fReader);
    }
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
        // for (auto [systName, systematic]: syst_by_name) {
        //     if (syst == systematic) {
        //         std::cout << "Systematic is: " << systName << std::endl;
        //         break;
        //     }
        // }
        std::vector<eVar> vars = (syst != Systematic::Nominal) ? syst_vars : nominal_var;
        for (auto var : vars) {
            // std::cout << "Variation is: " << varName_by_var.at(var) << std::endl;
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

void BaseSelector::SetupEvent(Systematic syst, eVar var, size_t systNum)
{
    SystematicWeights::currentSyst = syst;
    SystematicWeights::currentVar = var;

    weight = &o_weight[systNum];
    currentChannel_ = &o_channels[systNum];

    (*weight) = isMC_ ? **genWeight : 1.0;

    if (isMC_) {
        rGen.createTopList();
        for(size_t i = 0; i < jet.size(); ++i) {
            float jecPt = jetCorrector.getJES(jet.pt(i), jet.eta(i));
            float genPt = (jet.genJetIdx->At(i) != -1) ? rGenJet.pt(jet.genJetIdx->At(i)) : -1.0;
            float jetpt = jetCorrector.getJER(jecPt, jet.eta(i), **rho, genPt);
        }
    }
    muon.setGoodParticles(systNum, jet);
    elec.setGoodParticles(systNum, jet);
    jet.setGoodParticles(systNum);
    setOtherGoodParticles(systNum);
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
    rGen.clear();
    rGenJet.clear();

    std::fill(o_weight.begin(), o_weight.end(), 1.);
}

void BaseSelector::setupSystematicInfo()
{
    std::string scaleDir = getenv("CMSSW_BASE");
    scaleDir += "/src/analysis_suite/data";

    SystematicWeights::nSyst = numSystematics();
    SystematicWeights::year_ = year_;
    SystematicWeights::scaleDir_ = scaleDir;
    SystematicWeights::f_scale_factors = new TFile((scaleDir + "/scale_factors/event_scalefactors.root").c_str());
    if (year_ == Year::yr2016) {
        SystematicWeights::yearStr_ = "2016";
    } else if (year_ == Year::yr2017) {
        SystematicWeights::yearStr_ = "2017";
    } else {
        SystematicWeights::yearStr_ = "2018";
    }
}
