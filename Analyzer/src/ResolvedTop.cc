#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

void ResolvedTop::setup(TTreeReader& fReader)
{
    Particle::setup("ResolvedTop", fReader);
    discriminator = new TTRArray<Float_t>(fReader, "ResolvedTop_discriminator");

    setup_map(Level::Loose);

    std::string workingPoint = "TWP";
    wp = wp_by_name.at(workingPoint);

    setSF<TH1F>("topSF_" + workingPoint + "_True", "topSF");
    setSF<TH1F>("topSF_" + workingPoint + "_Fake", "fakeTopSF");
}

void ResolvedTop::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (discriminator->At(i) > wp)
            m_partList[Level::Loose]->push_back(i);
    }
}

float ResolvedTop::getScaleFactor(const Particle& genPart)
{
    float weight = 1.;
    for (auto tidx : list(Level::Loose)) {
        bool foundMatch = false;
        float minDR = 0.1;
        for (auto gidx : genPart.list(Level::Top)) {
            float dr2 = pow(genPart.eta(gidx) - eta(tidx), 2)
                + pow(genPart.phi(gidx) - phi(tidx), 2);
            if (dr2 < minDR) {
                foundMatch = true;
                weight *= getWeight("topSF", pt(tidx));
                break;
            }
        }
        if (!foundMatch) {
            weight *= getWeight("fakeTopSF", pt(tidx));
        }
    }
    return weight;
}
