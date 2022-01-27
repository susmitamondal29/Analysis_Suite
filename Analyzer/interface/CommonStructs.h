#ifndef COMMONSTRUCTS_H_
#define COMMONSTRUCTS_H_

#include "analysis_suite/Analyzer/interface/Variable.h"

#include "TSelectorList.h"
#include "TH1.h"

#include <set>

enum class Channel;
enum class Subchannel;

struct TriggerInfo {
    std::unordered_map<Subchannel, std::vector<std::string>> trigger_names;
    std::unordered_map<Subchannel, std::vector<TRVariable<Bool_t>>> trigs;
    std::unordered_map<std::string, std::string> l1_by_trig;

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

    bool pass_ind_cut(Subchannel chan, std::string trig_name) {
        for (size_t i=0; i < trigger_names[chan].size(); ++i) {
            if (trigger_names[chan][i] == trig_name) {
                return *trigs[chan][i];
            }
        }
        return false;
    }

    void add_l1seed(std::string trigname, std::string l1seed) {
        l1_by_trig[trigname] = l1seed;
    }

    void add_l1seeds(std::vector<std::string> trignames, std::string l1seed) {
        for (auto trigname: trignames) {
            l1_by_trig[trigname] = l1seed;
        }
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

    TreeInfo(std::string name, std::set<Channel> goodChannels_, TDirectory* outdir, TSelectorList* fOutput);

    void fillCutFlow(CutInfo& cuts, Channel chan, float weight);
    bool contains(Channel chan) { return goodChannels.count(chan); }
};




#endif // COMMONSTRUCTS_H_
