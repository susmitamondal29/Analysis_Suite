#include "analysis_suite/Analyzer/interface/Particle.h"

size_t Particle::nSyst = 0;

Particle::Particle() {}

void Particle::setup(std::string name, TTreeReader& fReader, int year)
{
    year_ = year;
    pt = new TTreeReaderArray<Float_t>(fReader, (name + "_pt").c_str());
    eta = new TTreeReaderArray<Float_t>(fReader, (name + "_eta").c_str());
    phi = new TTreeReaderArray<Float_t>(fReader, (name + "_phi").c_str());
    mass = new TTreeReaderArray<Float_t>(fReader, (name + "_mass").c_str());
}
