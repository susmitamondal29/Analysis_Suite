#ifndef __GENPARTICLE_H_
#define __GENPARTICLE_H_

#include "analysis_suite/Analyzer/interface/Particle.h"

class GenParticle : public Particle {
public:
    void setup(TTreeReader& fReader, int year, bool isMC);
    void createLooseList();
    void setGoodParticles(size_t syst)
    {
        if (!isMC)
            return;
        topList = &topArray[syst];
        createLooseList();
    }

    void clear()
    {
        for (size_t i = 0; i < nSyst; ++i) {
            topArray[i].clear();
        }
    }

    PartList topArray;
    std::vector<size_t>* topList;

    TTRArray<Int_t>* pdgId;
    bool isMC = true;
};

#endif // __GENPARTICLE_H_
