#include "analysis_suite/Analyzer/interface/Output.h"
#include"analysis_suite/Analyzer/interface/logging.h"

void fillJet(const Jet& jet, Level level, JetOut& fillObject, size_t pass_bitmap)
{
    LOG_FUNC << "Start fillJet";
    fillObject.clear();

    for (size_t idx = 0; idx < jet.size(); ++idx) {
        size_t final_bitmap = fillParticle(jet, level, fillObject, idx, pass_bitmap);
        if (final_bitmap != 0) {
            fillObject.discriminator.push_back(jet.btag->At(idx));
            fillObject.jer.push_back(jet.get_JEC_pair(Systematic::Jet_JER, idx));
            fillObject.jes.push_back(jet.get_JEC_pair(Systematic::Jet_JES, idx));
        }
    }
    LOG_FUNC << "End of fillJet";
}

void fillBJet(const Jet& jet, Level level, BJetOut& fillObject, size_t pass_bitmap)
{
    LOG_FUNC << "Start fillBJet";
    fillObject.clear();
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
            fillObject.jer.push_back(jet.get_JEC_pair(Systematic::Jet_JER, idx));
            fillObject.jes.push_back(jet.get_JEC_pair(Systematic::Jet_JES, idx));
        }
    }
    LOG_FUNC << "End of fillBJet";
}

void fillTop(const ResolvedTop& top, Level level, TopOut& fillObject, size_t pass_bitmap)
{
    LOG_FUNC << "Start of fillTop";
    fillObject.clear();
    for (size_t idx = 0; idx < top.size(); ++idx) {
        size_t final_bitmap = fillParticle(top, level, fillObject, idx, pass_bitmap);
        if (final_bitmap != 0) {
            fillObject.discriminator.push_back(top.discriminator->At(idx));
        }
    }
    LOG_FUNC << "End of fillTop";
}

void fillLeptons(const Lepton& muon, const Lepton& elec, ParticleOut& fillObject, size_t pass_bitmap)
{
    LOG_FUNC << "Start of fillLeptons";
    fillObject.clear();
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
    LOG_FUNC << "End of fillLeptons";
}
