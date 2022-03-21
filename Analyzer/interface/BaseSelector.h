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
#include "analysis_suite/Analyzer/interface/CommonStructs.h"

enum class Channel;
enum class Subchannel;

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
    std::vector<TreeInfo> getTrees() {
        std::vector<TreeInfo> tree_vec;
        for (auto& [chan, tree]: trees) {
            tree_vec.push_back(tree);
        }
        return tree_vec;
    }
    TDirectory* getOutdir() { return outdir; }

    ClassDef(BaseSelector, 0);

protected:
    size_t numSystematics() { return systematics_.size()*2 - 1; }
    virtual void clearParticles();
    virtual void clearOutputs(){};

    void createTree(std::string name, Channel chan)
    {
        trees.emplace(chan, TreeInfo(name, outdir, fOutput));
        SetupOutTreeBranches(trees.at(chan).tree);
    }

    void setupTrigger(Subchannel sChan, std::vector<std::string> trigs = {}) {
        trig_cuts.setup_channel(sChan, fReader, trigs);
    }

    void fillCutFlow(Channel chan, CutInfo& cuts) {
        if (trees.find(chan) != trees.end())
            trees.at(chan).fillCutFlow(cuts, *weight);
    }

    bool passMetFilters() {
        for (auto filter: metfilters) {
            if (!*filter) return false;
        }
        return true;
    }

    size_t nLeps(Level level) { return muon.size(level) + elec.size(level); }

    // To be filled by Child class
    virtual void ApplyScaleFactors(){};
    virtual void FillValues(const std::vector<bool>& passVec);
    virtual void setupChannel(){};
    virtual void setOtherGoodParticles(size_t syst){};
    virtual bool getCutFlow() { return true; }
    virtual void SetupOutTreeBranches(TTree* tree);

    // Protected Variables
    TTreeReader fReader;
    std::string groupName_;
    TFile* outfile;

    std::map<Channel, TreeInfo> trees;

    TRVariable<Float_t> genWeight;
    JetCorrection jetCorrector;

    Year year_;
    bool isMC_ = true;
    Channel channel_;
    Subchannel subChannel_;
    std::unordered_map<Subchannel, std::string> subchan_names;

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

    std::vector<TRVariable<Bool_t>> metfilters;

    ScaleFactors sfMaker;
    Muon muon;
    Electron elec;
    Jet jet;
    GenParticle rGen;
    GenJet rGenJet;

    TH1F *cutFlow, *cutFlow_individual;
    TriggerInfo trig_cuts;

private:
    void SetupEvent(Systematic syst, eVar var, size_t systNum);
    void setupSystematicInfo();
    void print_bar();

    std::vector<Systematic> systematics_ = { Systematic::Nominal };
    TDirectory* outdir;

    size_t passed_events = 0;
    size_t total_events = 0;
    size_t current_event = 0;
    const size_t barWidth  = 75;
};

#endif
