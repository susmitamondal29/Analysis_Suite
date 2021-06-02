#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

void ResolvedTop::setup(TTreeReader& fReader)
{
    Particle::setup("ResolvedTop", fReader);
    discriminator = new TTRArray<Float_t>(fReader, "ResolvedTop_discriminator");

    setup_map(Level::Loose);

    std::string workingPoint = "TWP";
    wp = wp_by_name.at(workingPoint);

    setSF(topSF, "topSF_" + workingPoint + "_True");
    setSF(fakeTopSF, "topSF_" + workingPoint + "_False");
}

void ResolvedTop::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (discriminator->At(i) > wp)
            m_partList[Level::Loose]->push_back(i);
    }
}

float ResolvedTop::getScaleFactor()
{
    float weight = 1.;
    // for (auto tidx : top.list(Level::Loose)) {
    //     bool foundMatch = false;
    //     float minDR = 0.1;
    //     float tpt = top.pt(tidx);
    //     float teta = top.eta(tidx);
    //     float tphi = top.phi(tidx);
    //     for (auto gidx : genPart.list(Level::Top)) {
    //         float dr2 = pow(genPart.eta(gidx) - teta, 2)
    //             + pow(genPart.phi(gidx) - tphi, 2);
    //         if (dr2 < minDR) {
    //             foundMatch = true;
    //             weight *= getWeight(topSF, tpt);
    //             break;
    //         }
    //     }
    //     if (!foundMatch) {
    //         weight *= getWeight(fakeTopSF, tpt);
    //     }
    // }
    return weight;
}
