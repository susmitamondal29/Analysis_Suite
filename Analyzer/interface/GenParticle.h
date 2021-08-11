#ifndef __GENPARTICLE_H_
#define __GENPARTICLE_H_

#include "analysis_suite/Analyzer/interface/Particle.h"

class GenParticle : public Particle {
public:
    void setup(TTreeReader& fReader);
    void createTopList();
    virtual void setupGoodLists() override
    {
        createTopList();
    }

    TTRArray<Int_t>* pdgId;
};

class GenJet : public Particle {
public:
    void setup(TTreeReader& fReader);
    void createJetList(Particle& jet);
    virtual void setupGoodLists(Particle& jet) override
    {
        createJetList(jet);
    }
};

#endif // __GENPARTICLE_H_
