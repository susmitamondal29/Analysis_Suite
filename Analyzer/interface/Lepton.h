#ifndef __LEPTON_H_
#define __LEPTON_H_

#include "analysis_suite/Analyzer/interface/Particle.h"
#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

#include <unordered_map>

class Lepton : public Particle {
public:
    virtual void createLooseList(){};
    virtual void createFakeList(Particle& jets){};
    virtual void createTightList(Particle& jets){};
    bool passZVeto();
    void setup(std::string name, TTreeReader& fReader);
    std::pair<size_t, float> getCloseJet(size_t lidx, const Particle& jet);
    bool passJetIsolation(size_t idx, const Particle& jets);
    Int_t charge(size_t idx) { return m_charge.at(idx); };
    Int_t charge(Level level, size_t i) { return charge(idx(level, i)); };
    float fakePt(size_t idx, const Particle& jets) const;
    float fakePt(Level level, size_t i, const Particle& jets) const { return fakePt(idx(level, i), jets); }
    float getMT(size_t idx, float met, float met_phi) const
    {
        return sqrt(2*pt(idx)*met*(1-cos(phi(idx) - met_phi)));
    }
    float getMT(Level level, size_t i, float met, float met_phi) const { return getMT(idx(level, i), met, met_phi); }

    virtual void setupGoodLists(Particle& jets) override
    {
        createLooseList();
        createFakeList(jets);
        createTightList(jets);
    }

    virtual void clear() override
    {
        Particle::clear();
        closeJet_by_lepton.clear();
    }

    std::unordered_map<size_t, size_t> closeJet_by_lepton;

    float isoCut, ptRatioCut, ptRelCut;

protected:
    TRArray<Int_t> m_charge;
    TRArray<Float_t> iso;
    TRArray<Float_t> dz;
    TRArray<Float_t> dxy;

    const float ZMASS = 91.188;
    const float ZWINDOW = 15;
    const float LOW_ENERGY_CUT = 12;
};

#endif // __LEPTON_H_
