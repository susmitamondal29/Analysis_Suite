#include "analysis_suite/Analyzer/interface/Output.h"

void fillBJet(Jet& jet, PartList& fillArray, BJetOut& fillObject)
{
    std::vector<Int_t> bitMap(jet.pt->GetSize());
    fillParticle(jet, fillArray, fillObject, bitMap);

    for (size_t syst = 0; syst < fillArray.size(); ++syst) {
        fillObject.n_loose.push_back(jet.n_loose_bjet.at(syst));
        fillObject.n_medium.push_back(jet.n_medium_bjet.at(syst));
        fillObject.n_tight.push_back(jet.n_tight_bjet.at(syst));
    }

    for (size_t idx = 0; idx < jet.pt->GetSize(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.discriminator.push_back(jet.btag->At(idx));
        }
    }
}

void fillTop(ResolvedTop& top, PartList& fillArray, TopOut& fillObject)
{
    std::vector<Int_t> bitMap(top.pt->GetSize());
    fillParticle(top, fillArray, fillObject, bitMap);

    for (size_t idx = 0; idx < top.pt->GetSize(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.discriminator.push_back(top.discriminator->At(idx));
        }
    }
}

void fillLeptons(Lepton& muon, Lepton& elec, ParticleOut& fillObject)
{
    size_t totLeptons = muon.pt->GetSize() + elec.pt->GetSize();
    std::vector<Int_t> bitMap(totLeptons);
    // for (size_t syst = 0; syst < Particle::nSyst; ++syst) {
    //     for (auto idx : fillArray[syst]) {
    //         bitMap[idx] += 1 << syst;
    //     }
    // }
    auto muonItr = muon.tightList->begin(), muonEnd = muon.tightList->end();
    auto elecItr = elec.tightList->begin(), elecEnd = elec.tightList->end();
    while (muonItr != muonEnd || elecItr != elecEnd) {
        if (muonItr != muonEnd && (elecItr == elecEnd || muon.pt->At(*muonItr) > elec.pt->At(*elecItr))) {
            fillObject.pt.push_back(muon.pt->At(*muonItr));
            fillObject.eta.push_back(muon.eta->At(*muonItr));
            fillObject.phi.push_back(muon.phi->At(*muonItr));
            fillObject.mass.push_back(muon.mass->At(*muonItr));
            muonItr++;
        } else {
            fillObject.pt.push_back(elec.pt->At(*elecItr));
            fillObject.eta.push_back(elec.eta->At(*elecItr));
            fillObject.phi.push_back(elec.phi->At(*elecItr));
            fillObject.mass.push_back(elec.mass->At(*elecItr));
            elecItr++;
        }
    }
}
