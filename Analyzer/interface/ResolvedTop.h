#ifndef __RESOLVEDTOP_H_
#define __RESOLVEDTOP_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

struct TopOut {
    std::vector<Float_t> pt;
    std::vector<Float_t> eta;
    std::vector<Float_t> phi;
    std::vector<Float_t> mass;
    std::vector<Float_t> discriminator;
    void clear() {
        pt.clear();
        eta.clear();
        phi.clear();
        mass.clear();
        discriminator.clear();
    }
};

class ResolvedTop : public Particle {
public:
    void setup(TTreeReader& fReader, int year);
    void createLooseList();
    void fillTop(std::vector<size_t>& fillList, TopOut& fillObject);
    void setupTops() {
        createLooseList();
    }

    void clear() {
        looseList.clear();
    }

    std::vector<size_t> looseList;

    TTRArray<Float_t>* discriminator;
};

#endif // __RESOLVEDTOP_H_
