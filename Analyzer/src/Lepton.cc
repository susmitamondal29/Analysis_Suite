#include "analysis_suite/Analyzer/interface/Lepton.h"
#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

#include <limits>

bool Lepton::useFakePt = false;

void Lepton::setup(std::string name, TTreeReader& fReader, bool isMC)
{
    m_charge.setup(fReader, name + "_charge");
    dz.setup(fReader, name + "_dz");
    dxy.setup(fReader, name + "_dxy");
    if (isMC) {
        genPartIdx.setup(fReader, name+"_genPartIdx");
    }

    // Isolation variables
    ptRel.setup(fReader, name + "_jetPtRelv2");
    ptRatio.setup(fReader, name + "_jetRelIso");
    iso.setup(fReader, name + "_miniPFRelIso_all");


    GenericParticle::setup(name, fReader);
    setup_map(Level::Loose);
    setup_map(Level::Fake);
    setup_map(Level::Tight);
}

std::pair<size_t, float> Lepton::getCloseJet(size_t lidx, const Particle& jet)
{
    size_t minIdx = SIZE_MAX;
    float minDr = 100;
    float lphi = phi(lidx);
    float leta = eta(lidx);
    for (size_t jidx = 0; jidx < jet.size(); jidx++) {
        float dr2 = deltaR(jet.eta(jidx), leta, jet.phi(jidx), lphi);
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
    for (auto tidx : list(Level::Loose)) { //tightList
        LorentzVector tlep = p4(tidx);
        for (auto lidx : list(Level::Loose)) {
            if (tidx >= lidx || charge(tidx) * charge(lidx) > 0)
                continue;
            float mass = (p4(lidx) + tlep).M();
            if (mass < LOW_ENERGY_CUT || (fabs(mass - ZMASS) < ZWINDOW))
                return false;
        }
    }
    return true;
}

bool Lepton::passZCut(float low, float high)
{
    for (auto tidx : list(Level::Fake)) { //tightList
        LorentzVector tlep = p4(tidx);
        for (auto lidx : list(Level::Fake)) {
            if (tidx >= lidx || charge(tidx) * charge(lidx) > 0)
                continue;
            float mass = (p4(lidx) + tlep).M();
            if (mass > low && mass < high)
                return true;
        }
    }
    return false;
}

bool Lepton::passJetIsolation(size_t idx, const Particle& jets)
{
    if (closeJet_by_lepton.find(idx) == closeJet_by_lepton.end())
        return true; /// no close jet (probably no jets)
    return iso.at(idx) < isoCut && ( 1/(1+ptRatio.at(idx)) > ptRatioCut || ptRel.at(idx) > ptRelCut );
}

float Lepton::fillFakePt(size_t idx, const Particle& jets) const
{
    if (closeJet_by_lepton.find(idx) == closeJet_by_lepton.end())
        return 1.; /// no close jet (probably no jets)
    auto jetV = jets.p3(closeJet_by_lepton.at(idx));

    if (ptRel.at(idx) > ptRelCut) {
        if (iso.at(idx) > isoCut)
            return (1 + iso.at(idx)-isoCut);
    } else if (1/(1+ptRatio.at(idx)) <= ptRatioCut) {
        return jetV.rho()*ptRatioCut/pt(idx);
    }
    return 1.;
}

void Lepton::fillFlippedCharge(GenParticle& gen)
{
    for (size_t i = 0; i < size(); i++) {
        int pdg = gen.pdgId.at(genPartIdx.at(i));
        // remember, pdg is postive for electron, negative for positron

        flips.push_back(abs(pdg) == static_cast<int>(id) && pdg*charge(i) > 0);
    }
}
