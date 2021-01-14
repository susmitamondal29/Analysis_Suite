#include "analysis_suite/Analyzer/interface/BaseSelector.h"
#include "TParameter.h"

void BaseSelector::Begin(TTree * /*tree*/)
{
    TString option = GetOption();
}

void BaseSelector::SlaveBegin(TTree * /*tree*/)
{
    if (GetInputList() != nullptr) {
        TParameter<bool>* applyScaleFactors = (TParameter<bool>*) GetInputList()->FindObject("applyScaleFacs");
        if (applyScaleFactors != nullptr && applyScaleFactors->GetVal()) {
            SetScaleFactors();
        }
    }
}

void BaseSelector::Init(TTree *tree)
{
    if (!tree) return;
    fChain = tree;
    fReader.SetTree(fChain);
    outTree = new TTree("test", "test");
    SetupOutTree();
    fOutput->Add(outTree);
    variations_.push_back(1);

    year_ = yr2018;
    
    muon.setup(fReader, year_);
    elec.setup(fReader, year_);
    jet.setup(fReader, year_);
}


void BaseSelector::SetScaleFactors() {
    std::invalid_argument("No scale factors defined for selector!");
}


Bool_t BaseSelector::Process(Long64_t entry)
{
    if (entry % 10000 == 0)
        std::cout << "At entry: " << entry << std::endl;
    fReader.SetLocalEntry(entry);
    for (const auto& variation : variations_) {
        SetupEvent(variation);
        if (passSelection(variation)) {
            FillValues(variation);
            outTree->Fill();
        }
    }

    return kTRUE;
}

Bool_t BaseSelector::Notify()
{
    return kTRUE;
}

float BaseSelector::GetPrefiringEfficiencyWeight(
    std::vector<float>* jetPt, std::vector<float>* jetEta) {
    float prefire_weight = 1;
    for (size_t i = 0; i < jetPt->size(); i++) {
        float jPt = jetPt->at(i);
        float jEta = std::abs(jetEta->at(i));
        prefire_weight *= (1-prefireEff_->GetEfficiency(prefireEff_->FindFixBin(jEta, jPt)));
    }
    return prefire_weight;
}

void BaseSelector::Terminate()
{
}

void BaseSelector::SlaveTerminate()
{
}

void BaseSelector::SetupEvent(int variation) {
    clearValues();

    muon.setupLepton(jet);
    elec.setupLepton(jet);
    jet.setupJet();

    setupChannel();

    if (isMC_) {
        ApplyScaleFactors();
    }

}
