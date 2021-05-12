#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "TParameter.h"

void BaseSelector::Begin(TTree* /*tree*/) { TString option = GetOption(); }

void BaseSelector::SlaveBegin(TTree* /*tree*/)
{
    if (GetInputList() != nullptr) {
        TParameter<bool>* applyScaleFactors = (TParameter<bool>*)GetInputList()->FindObject("applyScaleFacs");
        if (applyScaleFactors != nullptr && applyScaleFactors->GetVal()) {
            SetScaleFactors();
        }
    }
}

void BaseSelector::Init(TTree* tree)
{
    if (!tree)
        return;
    fChain = tree;
    fReader.SetTree(fChain);
    for (auto item : *fInput) {
        fOutput->Add(item);
        if (strcmp(item->GetName(), "Year") == 0) {
            year_ = yearMap[item->GetTitle()];
        } else if (strcmp(item->GetName(), "xsec") == 0) {
            xsec_ = std::stof(item->GetTitle());
        }
    }

    sfMaker = ScaleFactors(year_);
    isMC_ = true;
    outTree = new TTree("Analyzed", "Analyzed");
    outTree->Branch("weight", &o_weight);
    outTree->Branch("PassEvent", &o_pass_event);

    SetupOutTree();
    fOutput->Add(outTree);

    if (isMC_) {
        genWeight = new TTreeReaderValue<Float_t>(fReader, "genWeight");
    }

    variations_.push_back("Nominal");
    // variations_.push_back("Other");
    Particle::nSyst = variations_.size();
    o_weight.resize(variations_.size());

    muon.setup(fReader, year_);
    elec.setup(fReader, year_);
    jet.setup(fReader, year_);
}

void BaseSelector::SetScaleFactors()
{
    std::invalid_argument("No scale factors defined for selector!");
}

Bool_t BaseSelector::Process(Long64_t entry)
{
    if (entry % 10000 == 0)
        std::cout << "At entry: " << entry << std::endl;

    clearValues();
    fReader.SetLocalEntry(entry);
    std::vector<bool> systPassSelection;
    bool passAny = false;
    for (size_t syst = 0; syst < variations_.size(); ++syst) {
        SetupEvent(syst);
        systPassSelection.push_back(passSelection() && passTrigger());
        passAny |= systPassSelection.back();
    }
    if (passAny) {
        o_pass_event = systPassSelection;
        FillValues(systPassSelection);
        outTree->Fill();
    }
    passed_events += systPassSelection.at(0);
    return kTRUE;
}

Bool_t BaseSelector::Notify() { return kTRUE; }

float BaseSelector::GetPrefiringEfficiencyWeight(std::vector<float>* jetPt,
    std::vector<float>* jetEta)
{
    float prefire_weight = 1;
    for (size_t i = 0; i < jetPt->size(); i++) {
        float jPt = jetPt->at(i);
        float jEta = fabs(jetEta->at(i));
        prefire_weight *= (1 - prefireEff_->GetEfficiency(prefireEff_->FindFixBin(jEta, jPt)));
    }
    return prefire_weight;
}

void BaseSelector::Terminate() {}

void BaseSelector::SlaveTerminate()
{
    std::cout << passed_events << " events passed selection" << std::endl;
}

void BaseSelector::SetupEvent(size_t syst)
{
    weight = &o_weight[syst];
    muon.setGoodParticles(jet, syst);
    elec.setGoodParticles(jet, syst);
    jet.setGoodParticles(syst);
    setOtherGoodParticles(syst);

    setupChannel();

    if (isMC_) {
        (*weight) = **genWeight;
        ApplyScaleFactors();
    }
}

void BaseSelector::clearValues()
{
    muon.clear();
    elec.clear();
    jet.clear();

    std::fill(o_weight.begin(), o_weight.end(), 1.);
}
