#ifndef __RESOLVEDTOP_H_
#define __RESOLVEDTOP_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

class ResolvedTop : public Particle {
public:
    void setup(TTreeReader& fReader, int year);
    void createLooseList();
    void setGoodParticles(size_t syst)
    {
        looseList = &looseArray[syst];
        createLooseList();
    }

    void clear()
    {
        for (size_t i = 0; i < nSyst; ++i) {
            looseArray[i].clear();
        }
    }

    PartList looseArray;
    std::vector<size_t>* looseList;

    TTRArray<Float_t>* discriminator;
};

#endif // __RESOLVEDTOP_H_
