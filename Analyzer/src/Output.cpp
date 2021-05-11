#include "analysis_suite/Analyzer/interface/Output.h"

void fillBJet(Jet& jet, int listName, BJetOut& fillObject, std::vector<bool> passVec)
{
    std::vector<Int_t> bitMap(jet.size());
    fillParticle(jet, listName, fillObject, bitMap, passVec);

    for (size_t syst = 0; syst < Particle::nSyst; ++syst) {
        fillObject.n_loose.push_back(jet.n_loose_bjet.at(syst));
        fillObject.n_medium.push_back(jet.n_medium_bjet.at(syst));
        fillObject.n_tight.push_back(jet.n_tight_bjet.at(syst));
    }

    for (size_t idx = 0; idx < jet.size(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.discriminator.push_back(jet.btag->At(idx));
        }
    }
}

void fillTop(ResolvedTop& top, int listName, TopOut& fillObject, std::vector<bool> passVec)
{
    std::vector<Int_t> bitMap(top.size());
    fillParticle(top, listName, fillObject, bitMap, passVec);

    for (size_t idx = 0; idx < top.size(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.discriminator.push_back(top.discriminator->At(idx));
        }
    }
}

void fillLeptons(Lepton& muon, Lepton& elec, ParticleOut& fillObject)
{
    // size_t tot = muon.size() + elec.size();

    // size_t midx, eidx;
    // while (midx != muon.size() && eidx != elec.size() ) {
    //     if (midx != muon.size() && (eidx == elec.size() ))
    //         }

    // std::vector<Int_t> bitMap(totLeptons);
    // for (size_t syst = 0; syst < Particle::nSyst; ++syst) {
    //     for (auto idx : fillArray[syst]) {
    //         bitMap[idx] += 1 << syst;
    //     }
    // }
    // auto muonItr = muon.tightList->begin(), muonEnd = muon.tightList->end();
    // auto elecItr = elec.tightList->begin(), elecEnd = elec.tightList->end();
    // while (muonItr != muonEnd || elecItr != elecEnd) {
    //     if (muonItr != muonEnd && (elecItr == elecEnd || muon.pt->At(*muonItr) > elec.pt->At(*elecItr))) {
    //         fillObject.pt.push_back(muon.pt->At(*muonItr));
    //         fillObject.eta.push_back(muon.eta->At(*muonItr));
    //         fillObject.phi.push_back(muon.phi->At(*muonItr));
    //         fillObject.mass.push_back(muon.mass->At(*muonItr));
    //         muonItr++;
    //     } else {
    //         fillObject.pt.push_back(elec.pt->At(*elecItr));
    //         fillObject.eta.push_back(elec.eta->At(*elecItr));
    //         fillObject.phi.push_back(elec.phi->At(*elecItr));
    //         fillObject.mass.push_back(elec.mass->At(*elecItr));
    //         elecItr++;
    //     }
    // }
}
