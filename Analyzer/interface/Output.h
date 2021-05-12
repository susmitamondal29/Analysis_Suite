#ifndef __OUTPUT_H_
#define __OUTPUT_H_

#include "analysis_suite/Analyzer/interface/Jet.h"
#include "analysis_suite/Analyzer/interface/Lepton.h"
#include "analysis_suite/Analyzer/interface/Particle.h"
#include "analysis_suite/Analyzer/interface/ResolvedTop.h"

struct ParticleOut {
    std::vector<Float_t> pt;
    std::vector<Float_t> eta;
    std::vector<Float_t> phi;
    std::vector<Float_t> mass;
    std::vector<Int_t> syst_bitMap;
    void clear()
    {
        pt.clear();
        eta.clear();
        phi.clear();
        mass.clear();
        syst_bitMap.clear();
    }
};

struct BJetOut {
    std::vector<Float_t> pt;
    std::vector<Float_t> eta;
    std::vector<Float_t> phi;
    std::vector<Float_t> mass;
    std::vector<Int_t> syst_bitMap;
    std::vector<Float_t> discriminator;
    std::vector<Int_t> n_loose;
    std::vector<Int_t> n_medium;
    std::vector<Int_t> n_tight;

    void clear()
    {
        pt.clear();
        eta.clear();
        phi.clear();
        mass.clear();
        syst_bitMap.clear();
        discriminator.clear();
        n_loose.clear();
        n_medium.clear();
        n_tight.clear();
    }
};

struct TopOut {
    std::vector<Float_t> pt;
    std::vector<Float_t> eta;
    std::vector<Float_t> phi;
    std::vector<Float_t> mass;
    std::vector<Int_t> syst_bitMap;
    std::vector<Float_t> discriminator;
    void clear()
    {
        pt.clear();
        eta.clear();
        phi.clear();
        mass.clear();
        syst_bitMap.clear();
        discriminator.clear();
    }
};

template <class T>
size_t fillParticle(Particle& particle, int listName, T& fillObject, size_t idx, size_t pass_bitmap);

template <class T>
void fillParticle(Particle& particle, int listName, T& fillObject, size_t pass_bitmap);

void fillBJet(Jet& jet, int listName, BJetOut& fillObject, size_t pass_bitmap);

void fillTop(ResolvedTop& top, int listName, TopOut& fillObject, size_t pass_bitmap);

void fillLeptons(Lepton& muon, Lepton& elec, ParticleOut& fillObject);

#include "analysis_suite/Analyzer/interface/Output.hxx"

#endif // __OUTPUT_H_
