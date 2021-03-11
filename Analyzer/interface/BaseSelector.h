#ifndef BASESELECTOR_H
#define BASESELECTOR_H

#include <TChain.h>
#include <TEfficiency.h>
#include <TFile.h>
#include <TROOT.h>
#include <TSelector.h>
#include <TTree.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <string.h>

#include <exception>
#include <iostream>
#include <unordered_map>
#include <vector>

#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include "analysis_suite/Analyzer/interface/Electron.h"
#include "analysis_suite/Analyzer/interface/Jet.h"
#include "analysis_suite/Analyzer/interface/Muon.h"

class BaseSelector : public TSelector {
public:
    TTree* fChain = 0; //! pointer to the analyzed TTree or TChain
    // Readers to access the data (delete the ones you do not need).
    BaseSelector(TTree* /*tree*/ = 0) {}
    virtual ~BaseSelector() {}
    virtual void SetScaleFactors();
    virtual Int_t Version() const { return 2; }
    virtual void Begin(TTree* tree);
    virtual void SlaveBegin(TTree* tree);
    virtual void Init(TTree* tree);
    virtual Bool_t Notify();
    virtual Bool_t Process(Long64_t entry);
    virtual Int_t GetEntry(Long64_t entry, Int_t getall = 0)
    {
        return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0;
    }
    virtual void SetOption(const char* option) { fOption = option; }
    virtual void SetObject(TObject* obj) { fObject = obj; }
    virtual void SetInputList(TList* input) { fInput = input; }
    virtual TList* GetOutputList() const { return fOutput; }
    virtual void SlaveTerminate();
    virtual void Terminate();

    virtual void SetupOutTree() {}
    void SetupEvent(int variation);
    virtual bool passSelection(int variations) { return true; }
    virtual void FillValues(int variation) {}
    virtual void setupChannel(){};
    virtual void setupParticles(){};
    virtual void ApplyScaleFactors(){};
    virtual void clearValues(){};
    ClassDef(BaseSelector, 0);

protected:
    float GetPrefiringEfficiencyWeight(std::vector<float>* jetPt, std::vector<float>* jetEta);
    std::vector<int> variations_;
    TEfficiency* prefireEff_;
    size_t passed_events = 0;
    TTreeReader fReader;
    std::unordered_map<std::string, int> yearMap = {
        { "2016", yr2016 }, { "2017", yr2017 }, { "2018", yr2018 }
    };
    int year_;
    float xsec_;
    TTree* outTree;
    TTreeReaderValue<Float_t> genWeight = { fReader, "genWeight" };
    float weight = 1;

    bool isMC_;
    int channel_, currentChannel_;

    Muon muon;
    Electron elec;
    Jet jet;
};

#endif
