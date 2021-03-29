#ifndef __GENPARTICLE_H_
#define __GENPARTICLE_H_

#include "analysis_suite/Analyzer/interface/Particle.h"

class GenParticle : public Particle {
public:
    void setup(TTreeReader& fReader, int year);
    void createLooseList();
    void setupParticles() {
        createLooseList();
    }

    void clear() {
        topList.clear();
    }

    std::vector<size_t> topList;

    TTRArray<Int_t>* pdgId;
};

 
#endif // __GENPARTICLE_H_
