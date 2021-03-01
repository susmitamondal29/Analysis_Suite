#include "analysis_suite/Analyzer/interface/Lepton.h"

#include <limits>

void Lepton::setup(std::string name, TTreeReader& fReader, int year)
{
    charge = new TTreeReaderArray<Int_t>(fReader, (name + "_charge").c_str());
    Particle::setup(name, fReader, year);
}

std::pair<size_t, float> Lepton::getCloseJet(size_t lidx, Particle& jet)
{
    size_t minIdx = SIZE_MAX;
    float minDr = 100;
    float lphi = phi->At(lidx);
    float leta = eta->At(lidx);
    for (size_t jidx = 0; jidx < jet.pt->GetSize(); jidx++) {
        float dr2 = pow(jet.eta->At(jidx) - leta, 2) + pow(jet.phi->At(jidx) - lphi, 2);
        if (minDr > dr2) {
            minIdx = jidx;
            minDr = dr2;
        }
    }

    if (minIdx != SIZE_MAX)
        closeJet_by_lepton[lidx] = minIdx;

    return std::make_pair(minIdx, minDr);
}

bool Lepton::passZVeto()
{
    for (auto tidx : tightList) {
        LorentzVector tlep(pt->At(tidx), eta->At(tidx), phi->At(tidx),
            mass->At(tidx));
        for (auto lidx : looseList) {
            if (tidx == lidx || charge->At(tidx) * charge->At(lidx) > 0)
                continue;
            LorentzVector llep(pt->At(lidx), eta->At(lidx), phi->At(lidx),
                mass->At(lidx));
            float mass = (llep + tlep).M();
            if (mass < LOW_ENERGY_CUT || (mass > ZMASS - ZWINDOW && mass < ZMASS + ZWINDOW))
                return false;
        }
    }
    return true;
}

bool Lepton::passJetIsolation(size_t idx, Particle& jets)
{
    if (closeJet_by_lepton.find(idx) == closeJet_by_lepton.end())
        return true; /// no close jet (probably no jets)
    size_t jidx = closeJet_by_lepton[idx];
    if (pt->At(idx) / jets.pt->At(jidx) > ptRatioCut)
        return true;

    LorentzVector lepV(pt->At(idx), eta->At(idx), phi->At(idx), mass->At(idx));
    LorentzVector jetV(jets.pt->At(jidx), jets.eta->At(jidx), jets.phi->At(jidx),
        jets.mass->At(jidx));
    auto diff = jetV.Vect() - lepV.Vect();
    auto cross = diff.Cross(lepV.Vect());
    return cross.Mag2() / diff.Mag2() > ptRelCut;
}
