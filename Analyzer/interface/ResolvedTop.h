#ifndef __RESOLVEDTOP_H_
#define __RESOLVEDTOP_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

class ResolvedTop : public Particle {
public:
    void setup(TTreeReader& fReader);
    void createLooseList();
    virtual float getScaleFactor() override;
    virtual void setGoodParticles(size_t syst) override
    {
        Particle::setGoodParticles(syst);
        createLooseList();

        fill_bitmap();
    }

    TTRArray<Float_t>* discriminator;

    TH1F *topSF, *fakeTopSF;

    const std::unordered_map<std::string, float> wp_by_name = {
        { "LWP", 0.75 }, // Loose 0.75
        { "MWP", 0.85 }, // Medium 0.85
        { "Alt_TWP", 0.92 }, // AltTight 0.92
        { "TWP", 0.95 }, // Tight 0.95
    };
    float wp;
};

#endif // __RESOLVEDTOP_H_
