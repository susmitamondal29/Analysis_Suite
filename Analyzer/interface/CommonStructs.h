#ifndef COMMONSTRUCTS_H_
#define COMMONSTRUCTS_H_

#include "analysis_suite/Analyzer/interface/Variable.h"

enum class Channel;
enum class Subchannel;

struct TriggerInfo {
    std::unordered_map<Subchannel, std::vector<std::string>> trigger_names;
    std::unordered_map<Subchannel, std::vector<TRVariable<Bool_t>>> trigs;

    void setup_channel(Subchannel chan, TTreeReader& fReader, std::vector<std::string> trigger_names_ = {}) {
        trigger_names[chan] = trigger_names_;
        trigs[chan] = std::vector<TRVariable<Bool_t>>();
        for (auto trig_name: trigger_names_) {
            trigs[chan].push_back(TRVariable<Bool_t>(fReader, trig_name));
        }
    }

    bool pass_cut(Subchannel chan) {
        if (trigs.find(chan) == trigs.end()) {
            return true;
        }

        for (auto trig : trigs[chan]) {
            if (*trig) return true;
        }
        return false;
    }

    std::vector<std::string> get_pass_list(Subchannel chan) {
        std::vector<std::string> trig_list;
        for (size_t i=0; i < trigger_names[chan].size(); ++i) {
            if (*trigs[chan].at(i)) {
                trig_list.push_back(trigger_names[chan].at(i));
            }
        }
        return trig_list;
    }
};

struct CutInfo {
    std::vector<std::pair<std::string, bool>> cuts;

    bool passCutFlow() {
        for (auto& [_, pass] : cuts) {
            if (!pass) return false;
        }
        return true;
    }

    bool setCut(std::string name, bool pass) {
        cuts.push_back(std::make_pair(name, pass));
        return pass;
    }

    size_t size() { return cuts.size(); }

    std::string name(size_t i) { return cuts.at(i).first; }

};



struct TreeInfo {
    TTree* tree;
    std::set<Channel> goodChannels;
    TH1F *cutflow, *cutflow_ind;
    bool initialize_axis = false;

    TreeInfo(TTree* tree_, std::set<Channel> goodChannels_, TSelectorList* fOutput) :
        tree(tree_), goodChannels(goodChannels_)
    {
        std::string treeName = tree->GetName();
        cutflow = new TH1F(("cutFlow_"+treeName).c_str(), ("cutFlow_"+treeName).c_str(),
                           15, 0, 15);
        fOutput->Add(cutflow);
        cutflow_ind = new TH1F(("cutFlow_ind_"+treeName).c_str(), ("cutFlow_ind_"+treeName).c_str(),
                               15, 0, 15);
        fOutput->Add(cutflow_ind);
    }
    bool contains(Channel chan) { return goodChannels.count(chan); }

    void fillCutFlow(CutInfo& cuts, Channel chan, float weight) {
        // Setup cutflow histogram
        if (!initialize_axis) {
            initialize_axis = true;
            for (size_t i = 0; i < cuts.size(); ++i) {
                cutflow->GetXaxis()->SetBinLabel(i+1, cuts.name(i).c_str());
                cutflow_ind->GetXaxis()->SetBinLabel(i+1, cuts.name(i).c_str());
            }
            cutflow->GetXaxis()->SetBinLabel(cuts.size()+1, "PassChannel");
            cutflow_ind->GetXaxis()->SetBinLabel(cuts.size()+1, "PassChannel");
        }

        bool passAll = true;
        for (auto& [cutName, truth] : cuts.cuts) {
            passAll &= truth;
            if (truth)
                cutflow_ind->Fill(cutName.c_str(), weight);
            if (passAll)
                cutflow->Fill(cutName.c_str(), weight);
        }
        if (contains(chan)) {
            cutflow_ind->Fill("PassChannel", weight);
            if (passAll)
                cutflow->Fill("PassChannel", weight);
        }
    }
};




#endif // COMMONSTRUCTS_H_
