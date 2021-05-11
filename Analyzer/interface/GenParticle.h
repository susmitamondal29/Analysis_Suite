#ifndef __GENPARTICLE_H_
#define __GENPARTICLE_H_

#include "analysis_suite/Analyzer/interface/Particle.h"

class GenParticle : public Particle {
public:
    void setup(TTreeReader& fReader, int year, bool isMC);
    void createLooseList();
    virtual void setGoodParticles(size_t syst) override
    {
        if (!isMC)
            return;
        Particle::setGoodParticles(syst);
        createLooseList();
    }

    TTRArray<Int_t>* pdgId;
    bool isMC = true;
};

#endif // __GENPARTICLE_H_
