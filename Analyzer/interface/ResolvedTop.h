#ifndef __RESOLVEDTOP_H_
#define __RESOLVEDTOP_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

class ResolvedTop : public Particle {
public:
    void setup(TTreeReader& fReader, int year);
    void createLooseList();
    template <class T>
    void fillTop(PartList& fillArray, T& fillObject);
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

template <class T>
void ResolvedTop::fillTop(PartList& fillArray, T& fillObject)
{
    std::vector<Int_t> bitMap(pt->GetSize());
    fillParticle(fillArray, fillObject, bitMap);

    for (size_t idx = 0; idx < pt->GetSize(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.discriminator.push_back(discriminator->At(idx));
        }
    }
}

#endif // __RESOLVEDTOP_H_
