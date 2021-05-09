#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

void ResolvedTop::setup(TTreeReader& fReader, int year)
{
    Particle::setup("ResolvedTop", fReader, year);
    discriminator = new TTRArray<Float_t>(fReader, "ResolvedTop_discriminator");
    // Loose 0.75
    // Medium 0.85
    // AltTight 0.92
    // Tight 0.95
    looseArray = PartList(nSyst);
}

void ResolvedTop::createLooseList()
{
    if (!pt)
        return;
    for (size_t i = 0; i < pt->GetSize(); i++) {
        if (discriminator->At(i) > 0.85)
            looseList->push_back(i);
    }
}
