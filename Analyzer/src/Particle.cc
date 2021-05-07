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

void Particle::fillParticle(std::vector<std::vector<size_t>>& fillList,
    ParticleOut& fillObject)
{
    std::vector<Int_t> bitMap(pt->GetSize());
    for (size_t syst = 0; syst < fillList.size(); ++syst) {
        for (auto idx : fillList[syst]) {
            fillObject.syst_bitMap[idx] += 1 << syst;
        }
    }
    for (size_t idx = 0; idx < pt->GetSize(); ++idx) {
        if (bitMap.at(idx) == 0) {
            continue;
        }
        fillObject.pt.push_back(pt->At(idx));
        fillObject.eta.push_back(eta->At(idx));
        fillObject.phi.push_back(phi->At(idx));
        fillObject.mass.push_back(mass->At(idx));
    }
    bitMap.erase(remove(bitMap.begin(), bitMap.end(), 0), bitMap.end());
    fillObject.syst_bitMap = bitMap;
}
