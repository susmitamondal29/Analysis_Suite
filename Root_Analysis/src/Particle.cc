#include "analysis_suite/Root_Analysis/interface/Particle.h"

Particle::Particle() {}

void Particle::setup(std::string name, TTreeReader& fReader, int year) {
    year_ = year;
    pt = new TTreeReaderArray<Float_t>(fReader, (name+"_pt").c_str());
    eta = new TTreeReaderArray<Float_t>(fReader, (name+"_eta").c_str());
    phi = new TTreeReaderArray<Float_t>(fReader, (name+"_phi").c_str());
    mass = new TTreeReaderArray<Float_t>(fReader, (name+"_mass").c_str());

}

void Particle::fillParticle(std::vector<size_t>& fillList, ParticleOut& fillObject) {
    for(auto midx: fillList) {
        fillObject.pt.push_back(pt->At(midx));
        fillObject.eta.push_back(eta->At(midx));
        fillObject.phi.push_back(phi->At(midx));
        fillObject.mass.push_back(mass->At(midx));
    }
}

