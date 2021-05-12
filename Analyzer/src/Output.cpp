#include "analysis_suite/Analyzer/interface/Output.h"

void fillBJet(Jet& jet, Level level, BJetOut& fillObject, size_t pass_bitmap)
{
    for (size_t syst = 0; syst < Particle::nSyst; ++syst) {
        if ((pass_bitmap >> syst) & 1) {
            fillObject.n_loose.push_back(jet.n_loose_bjet.at(syst));
            fillObject.n_medium.push_back(jet.n_medium_bjet.at(syst));
            fillObject.n_tight.push_back(jet.n_tight_bjet.at(syst));
        }
    }

    for (size_t idx = 0; idx < jet.size(); ++idx) {
        size_t final_bitmap = fillParticle(jet, level, fillObject, idx, pass_bitmap);
        if (final_bitmap != 0) {
            fillObject.discriminator.push_back(jet.btag->At(idx));
        }
    }
}

void fillTop(ResolvedTop& top, Level level, TopOut& fillObject, size_t pass_bitmap)
{
    for (size_t idx = 0; idx < top.size(); ++idx) {
        size_t final_bitmap = fillParticle(top, level, fillObject, idx, pass_bitmap);
        if (final_bitmap != 0) {
            fillObject.discriminator.push_back(top.discriminator->At(idx));
        }
    }
}

void fillLeptons(Lepton& muon, Lepton& elec, ParticleOut& fillObject, size_t pass_bitmap)
{
    size_t midx = 0;
    size_t eidx = 0;
    while (midx != muon.size() || eidx != elec.size()) {
        if (midx != muon.size() && (eidx == elec.size() || muon.pt(midx) > elec.pt(eidx))) {
            fillParticle(muon, Level::Tight, fillObject, midx, pass_bitmap);
            midx++;
        } else {
            fillParticle(elec, Level::Tight, fillObject, eidx, pass_bitmap);
            eidx++;
        }
    }
}
