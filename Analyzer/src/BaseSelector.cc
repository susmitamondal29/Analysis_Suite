#include "analysis_suite/Analyzer/interface/BaseSelector.h"

#include "analysis_suite/Analyzer/interface/SystematicMaker.h"

size_t BaseSelector::numSystematics()
{
    size_t total = 0;
    for (auto syst : systematics_) {
        total += var_by_syst.at(syst).size();
    }
    return total;
};

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
                    std::cout << data->GetTitle() << std::endl;
                    isMC_ = static_cast<std::string>(data->GetTitle()) == "False";
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

    sfMaker = ScaleFactors(year_);
    systMaker = new SystematicMaker(this, year_);

    createObject(outTree, "Analyzed");
    outTree->Branch("weight", &o_weight);
    outTree->Branch("PassEvent", &o_pass_event);
    SetupOutTree();

    fReader.SetTree(tree);
    if (isMC_) {
        std::cout << "here" << std::endl;
        genWeight = new TTreeReaderValue<Float_t>(fReader, "genWeight");
        LHEScaleWeight = new TTRArray<Float_t>(fReader, "LHEScaleWeight");
    }

    o_weight.resize(numSystematics());

    setupParticleInfo();
    muon.setup(fReader);
    elec.setup(fReader);
    jet.setup(fReader, isMC_);
}

Bool_t BaseSelector::Process(Long64_t entry)
{
    if (entry % 10000 == 0)
        std::cout << "At entry: " << entry << std::endl;

    clearValues();
    fReader.SetLocalEntry(entry);
    std::vector<bool> systPassSelection;
    bool passAny = false;
    size_t systNum = 0;
    for (auto syst : systematics_) {
        for (auto var : var_by_syst.at(syst)) {
            SetupEvent(syst, var, systNum);
            systPassSelection.push_back(passSelection());
            if (syst == Systematic::Nominal) {
                fillCutFlow();
            }
            passAny |= systPassSelection.back();
            systNum++;
        }
    }
    if (passAny) {
        o_pass_event = systPassSelection;
        FillValues(systPassSelection);
        outTree->Fill();
    }
    passed_events += systPassSelection.at(0);
    return kTRUE;
}

void BaseSelector::SlaveTerminate()
{
    std::cout << passed_events << " events passed selection" << std::endl;
}

void BaseSelector::SetupEvent(Systematic syst, Variation var, size_t systNum)
{
    weight = &o_weight[systNum];
    (*weight) = isMC_ ? **genWeight : 1.0;

    muon.setGoodParticles(jet, systNum);
    elec.setGoodParticles(jet, systNum);
    jet.setGoodParticles(systNum);
    setOtherGoodParticles(systNum);

    systMaker->applySystematic(syst, var);

    setupChannel();

    if (isMC_) {
        ApplyScaleFactors();
    }
}

void BaseSelector::clearValues()
{
    muon.clear();
    elec.clear();
    jet.clear();

    cuts.clear();

    std::fill(o_weight.begin(), o_weight.end(), 1.);
}

void BaseSelector::setupParticleInfo()
{
    Particle::nSyst = numSystematics();
    Particle::year_ = year_;
    std::string scaleDir = getenv("CMSSW_BASE");
    scaleDir += "/src/analysis_suite/data/scale_factors/";
    Particle::scaleDir_ = scaleDir;
    Particle::f_scale_factors = new TFile((scaleDir + "event_scalefactors.root").c_str());
    if (year_ == Year::yr2016) {
        Particle::yearStr_ = "2016";
    } else if (year_ == Year::yr2017) {
        Particle::yearStr_ = "2017";
    } else {
        Particle::yearStr_ = "2018";
    }
}
