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
#include "analysis_suite/Analyzer/interface/GenParticle.h"
#include "analysis_suite/Analyzer/interface/ScaleFactors.h"
#include "analysis_suite/Analyzer/interface/JetCorrection.h"
#include "analysis_suite/Analyzer/interface/Variable.h"

enum class Channel;
enum class Subchannel;

struct TreeInfo {
    TTree* tree;
    std::set<Channel> goodChannels;
    bool contains(Channel chan) { return goodChannels.count(chan); }
};

typedef std::vector<std::pair<std::string, bool>> cut_info;
template <class T>
using TTRValue = TTreeReaderValue<T>;

class BaseSelector : public TSelector {
    friend class ScaleFactors;

public:
    BaseSelector(TTree* /*tree*/ = 0) {}
    virtual ~BaseSelector() {}
    virtual Int_t Version() const { return 2; }

    virtual void Init(TTree* tree);
    virtual Bool_t Process(Long64_t entry);
    virtual void SlaveTerminate();

    void setOutputFile(TFile* outfile_) { outfile = outfile_; }
    std::vector<TreeInfo> getTrees() { return trees; }
    TDirectory* getOutdir() { return outdir; }

    ClassDef(BaseSelector, 0);

protected:
    size_t numSystematics();
    virtual void clearParticles();
    virtual void clearOutputs(){};

    template <class T, class... Args>
    void createObject(T*& obj, std::string name, Args... args)
    {
        obj = new T(name.c_str(), name.c_str(), args...);
        fOutput->Add(obj);
    }

    void createTree(std::string name, std::set<Channel> chans)
    {
        TTree* tree = new TTree(name.c_str(), name.c_str());
        tree->SetDirectory(outdir);
        trees.push_back({ tree, chans });
        SetupOutTreeBranches(tree);
    }

    bool passCutFlow(cut_info cuts) {
        for (auto& [cutName, pass] : cuts) {
            if (!pass) return false;
        }
        return true;
    }
    bool setCut(cut_info& cuts, std::string name, bool pass) {
        cuts.push_back(std::make_pair(name, pass));
        return pass;
    }
    void setupTrigger(Subchannel sChan, std::vector<std::string> trigs = {}) {
        trig_cuts[sChan] = std::vector<TTRValue<Bool_t>*>();
        for (auto trig: trigs) {
            trig_cuts[sChan].push_back(new TTRValue<Bool_t>(fReader, trig.c_str()));
        }
    }
    bool chanInSR(Channel chan) { return trees.at(0).contains(chan); }


    // To be filled by Child class
    virtual void fillTriggerEff(bool passCuts, bool passTrigger) {};
    virtual void ApplyScaleFactors(){};
    virtual void FillValues(const std::vector<bool>& passVec);
    virtual void setupChannel(){};
    virtual void setOtherGoodParticles(size_t syst){};
    virtual bool getCutFlow(cut_info& cuts) { return true; }
    virtual bool getTriggerCut(cut_info& cuts);
    virtual void SetupOutTreeBranches(TTree* tree);

    // Protected Variables
    TTreeReader fReader;
    std::string groupName_;
    TFile* outfile;

    std::vector<TreeInfo> trees;

    TRVariable<Float_t> genWeight;
    JetCorrection jetCorrector;

    Year year_;
    bool isMC_ = true;
    Channel channel_;
    Subchannel subChannel_;

    // Current weight and all weights
    float* weight;
    std::vector<Float_t> o_weight;

    // Current channel and all channels
    Channel* currentChannel_;
    std::vector<Channel> o_channels;

    std::vector<Bool_t> o_pass_event;
    TRVariable<UInt_t> run, lumiblock;
    UInt_t o_run, o_lumiblock;
    TRVariable<ULong64_t> event;
    ULong64_t o_event;

    ScaleFactors sfMaker;
    Muon muon;
    Electron elec;
    Jet jet;
    GenParticle rGen;
    GenJet rGenJet;

    TH1F *cutFlow, *cutFlow_individual;
    std::unordered_map<Subchannel, std::vector<TTRValue<Bool_t>*>> trig_cuts;

private:
    void SetupEvent(Systematic syst, eVar var, size_t systNum);
    void setupSystematicInfo();
    void fillCutFlow(cut_info& cuts);

    std::vector<Systematic> systematics_ = { Systematic::Nominal };
    size_t passed_events = 0;
    TDirectory* outdir;
};

#endif
