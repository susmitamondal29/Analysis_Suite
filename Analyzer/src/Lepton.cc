#include "analysis_suite/Analyzer/interface/Lepton.h"

#include <limits>

void Lepton::setup(std::string name, TTreeReader& fReader, int year)
{
    m_charge = new TTreeReaderArray<Int_t>(fReader, (name + "_charge").c_str());
    Particle::setup(name, fReader, year);
    looseArray = PartList(nSyst);
    fakeArray = PartList(nSyst);
    tightArray = PartList(nSyst);
}

std::pair<size_t, float> Lepton::getCloseJet(size_t lidx, Particle& jet)
{
    size_t minIdx = SIZE_MAX;
    float minDr = 100;
    float lphi = phi(lidx);
    float leta = eta(lidx);
    for (size_t jidx = 0; jidx < jet.size(); jidx++) {
        float dr2 = pow(jet.eta(jidx) - leta, 2) + pow(jet.phi(jidx) - lphi, 2);
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
    for (auto tidx : *looseList) { //tightList
        LorentzVector tlep(pt(tidx), eta(tidx), phi(tidx),
            mass(tidx));
        for (auto lidx : *looseList) {
            if (tidx >= lidx || charge(tidx) * charge(lidx) > 0)
                continue;
            LorentzVector llep(pt(lidx), eta(lidx), phi(lidx),
                mass(lidx));
            float mass = (llep + tlep).M();
            if (mass < LOW_ENERGY_CUT || (fabs(mass - ZMASS) < ZWINDOW))
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
    if (pt(idx) / jets.pt(jidx) > ptRatioCut)
        return true;

    LorentzVector lepV(pt(idx), eta(idx), phi(idx), mass(idx));
    LorentzVector jetV(jets.pt(jidx), jets.eta(jidx), jets.phi(jidx), jets.mass(jidx));
    auto diff = jetV.Vect() - lepV.Vect();
    auto cross = diff.Cross(lepV.Vect());
    return cross.Mag2() / diff.Mag2() > ptRelCut;
}
