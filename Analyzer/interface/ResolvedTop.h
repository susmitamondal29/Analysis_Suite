#ifndef __RESOLVEDTOP_H_
#define __RESOLVEDTOP_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

class ResolvedTop : public Particle {
public:
    void setup(TTreeReader& fReader);
    void createLooseList();
    float getScaleFactor(const Particle& genPart);

    virtual void setupGoodLists() override
    {
        createLooseList();
    }

    TRArray<Float_t> mass_softdrop;
    TRArray<Float_t> tau2;
    TRArray<Float_t> tau3;

    const std::unordered_map<std::string, float> wp_by_name = {
        { "VL", 0.69 }, // Loose 5%
        { "L", 0.61 }, // Medium 2.5%
        { "M", 0.52 }, // AltTight 1%
        { "T", 0.47 }, // Tight 0.5%
        { "VT", 0.38 }, // Very tight 0.1%
    };
    float wp;
};

#endif // __RESOLVEDTOP_H_
