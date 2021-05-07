#ifndef __LEPTON_H_
#define __LEPTON_H_

#include "analysis_suite/Analyzer/interface/Particle.h"

#include <unordered_map>

class Lepton : public Particle {
public:
    void setup(std::string name, TTreeReader& fReader);
    virtual void createLooseList(){};
    virtual void createFakeList(Particle& jets){};
    virtual void createTightList(){};
    bool passZVeto();
    void setup(std::string name, TTreeReader& fReader, int year);
    std::pair<size_t, float> getCloseJet(size_t lidx, Particle& jet);
    bool passJetIsolation(size_t idx, Particle& jets);

    void setGoodParticles(Particle& jets)
    {
        createLooseList();
        createFakeList(jets);
        createTightList();
    }

    void clear()
    {
        for (size_t i = 0; i < nSyst; ++i) {
            looseArray[i].clear();
            fakeArray[i].clear();
            tightArray[i].clear();
        }

        closeJet_by_lepton.clear();
    }

    PartList looseArray;
    PartList fakeArray;
    PartList tightArray;
    vector<size_t>& looseList;
    vector<size_t>& fakeList;
    vector<size_t>& tightList;

    std::unordered_map<size_t, size_t> closeJet_by_lepton;

    TTRArray<Int_t>* charge;

    const float ZMASS = 91.188;
    const float ZWINDOW = 15;
    const float LOW_ENERGY_CUT = 12;

    float ptRatioCut, ptRelCut;
};

#endif // __LEPTON_H_
