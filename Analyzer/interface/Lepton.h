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
    Int_t charge(size_t idx) { return m_charge->At(idx); };

    void setGoodParticles(Particle& jets, size_t syst) 
    {
        Particle::setGoodParticles(syst);
        createLooseList();
        createFakeList(jets);
        createTightList();
    }

    virtual void clear() override
    {
        Particle::clear();
        closeJet_by_lepton.clear();
    }

    std::unordered_map<size_t, size_t> closeJet_by_lepton;

    float ptRatioCut, ptRelCut;

protected:
    TTRArray<Int_t>* m_charge;

    const float ZMASS = 91.188;
    const float ZWINDOW = 15;
    const float LOW_ENERGY_CUT = 12;
};

#endif // __LEPTON_H_
