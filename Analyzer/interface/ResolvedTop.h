#ifndef __RESOLVEDTOP_H_
#define __RESOLVEDTOP_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

class ResolvedTop : public Particle {
public:
    void setup(TTreeReader& fReader, Year year);
    void createLooseList();
    virtual void setGoodParticles(size_t syst) override
    {
        Particle::setGoodParticles(syst);
        createLooseList();

        fill_bitmap();
    }

    TTRArray<Float_t>* discriminator;
};

#endif // __RESOLVEDTOP_H_
