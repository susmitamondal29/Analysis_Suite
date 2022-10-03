#ifndef __GENPARTICLE_H_
#define __GENPARTICLE_H_

#include "analysis_suite/skim/interface/Particle.h"

class GenParticle : public GenericParticle {
public:
    void setup(TTreeReader& fReader);
    void createTopList();

    TRArray<Int_t> pdgId;
};

class GenJet : public GenericParticle {
public:
    void setup(TTreeReader& fReader);
};

#endif // __GENPARTICLE_H_
