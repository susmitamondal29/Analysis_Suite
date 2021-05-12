#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

void ResolvedTop::setup(TTreeReader& fReader, Year year)
{
    Particle::setup("ResolvedTop", fReader, year);
    discriminator = new TTRArray<Float_t>(fReader, "ResolvedTop_discriminator");
    // Loose 0.75
    // Medium 0.85
    // AltTight 0.92
    // Tight 0.95
    setup_map(Level::Loose);
}

void ResolvedTop::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (discriminator->At(i) > 0.85)
            list(Level::Loose)->push_back(i);
    }
}
