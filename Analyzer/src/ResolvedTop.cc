#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

void ResolvedTop::setup(TTreeReader& fReader, int year)
{
    Particle::setup("ResolvedTop", fReader, year);
    discriminator = new TTRArray<Float_t>(fReader, "ResolvedTop_discriminator");
    // Loose 0.75
    // Medium 0.85
    // AltTight 0.92
    // Tight 0.95
}

void ResolvedTop::createLooseList()
{
    if (!pt)
        return;
    for (size_t i = 0; i < pt->GetSize(); i++) {
        if (discriminator->At(i) > 0.85)
            looseList.push_back(i);
    }
}

void ResolvedTop::fillTop(std::vector<size_t>& fillList, TopOut& fillObject)
{
    for (auto midx : fillList) {
        fillObject.pt.push_back(pt->At(midx));
        fillObject.eta.push_back(eta->At(midx));
        fillObject.phi.push_back(phi->At(midx));
        fillObject.mass.push_back(mass->At(midx));
        fillObject.discriminator.push_back(discriminator->At(midx));
    }
}
