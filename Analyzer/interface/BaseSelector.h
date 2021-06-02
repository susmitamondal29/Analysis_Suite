#ifndef BASESELECTOR_H
#define BASESELECTOR_H

#include <TSelector.h>
#include <TTree.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>

#include <exception>
#include <iostream>
#include <unordered_map>
#include <vector>

#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include "analysis_suite/Analyzer/interface/Electron.h"
#include "analysis_suite/Analyzer/interface/Jet.h"
#include "analysis_suite/Analyzer/interface/Muon.h"
#include "analysis_suite/Analyzer/interface/ScaleFactors.h"

enum class Channel;
class SystematicMaker;

class BaseSelector : public TSelector {
    friend SystematicMaker;

public:
    BaseSelector(TTree* /*tree*/ = 0) {}
    virtual ~BaseSelector() {}
    virtual Int_t Version() const { return 2; }

    virtual void Init(TTree* tree);
    virtual Bool_t Process(Long64_t entry);
    virtual void SlaveTerminate();

    ClassDef(BaseSelector, 0);

protected:
    size_t numSystematics();
    virtual void clearValues();

    template <class T, class... Args>
    void createObject(T*& obj, std::string name, Args... args)
    {
        obj = new T(name.c_str(), name.c_str(), args...);
        fOutput->Add(obj);
    }

    // To be filled by Child class
    virtual void fillCutFlow(){};
    virtual void ApplyScaleFactors(){};
    virtual void FillValues(const std::vector<bool>& passVec) {}
    virtual void setupChannel(){};
    virtual void setOtherGoodParticles(size_t syst){};
    virtual bool passSelection() { return true; }
    virtual void SetupOutTree() {}

    // Protected Variables
    TTreeReader fReader;
    TTree* outTree;

    TTreeReaderValue<Float_t>* genWeight;
    TTreeReaderArray<Float_t>* LHEScaleWeight;

    float* weight;
    Year year_;
    bool passTrigger;
    bool isMC_ = true;
    Channel channel_, currentChannel_;

    std::vector<Float_t> o_weight;
    std::vector<Bool_t> o_pass_event;
    std::vector<std::pair<std::string, bool>> cuts;

    ScaleFactors sfMaker;
    SystematicMaker* systMaker;
    Muon muon;
    Electron elec;
    Jet jet;

private:
    void SetupEvent(Systematic syst, Variation var, size_t systNum);
    void setupParticleInfo();

    std::vector<Systematic> systematics_ = { Systematic::Nominal };
    size_t passed_events = 0;

    float xsec_;
};

#endif
