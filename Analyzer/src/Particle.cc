#include "analysis_suite/Analyzer/interface/Particle.h"

size_t Particle::nSyst = 0;

Particle::Particle() {}

void Particle::setup(std::string name, TTreeReader& fReader, int year)
{
    year_ = year;
    m_pt = new TTreeReaderArray<Float_t>(fReader, (name + "_pt").c_str());
    m_eta = new TTreeReaderArray<Float_t>(fReader, (name + "_eta").c_str());
    m_phi = new TTreeReaderArray<Float_t>(fReader, (name + "_phi").c_str());
    m_mass = new TTreeReaderArray<Float_t>(fReader, (name + "_mass").c_str());
}

void Particle::clear()
{
    for (auto& [key, plist] : m_partArray) {
        m_bitArray[key].clear();
        for (size_t i = 0; i < nSyst; ++i) {
            plist[i].clear();
        }
    }
}

void Particle::setGoodParticles(size_t syst)
{
    for (auto& [key, plist] : m_partArray) {
        m_partList[key] = &plist[syst];
        m_bitArray[key].assign(size(), 0);
    }
}

void Particle::fill_bitmap()
{
    for (const auto& [key, plist] : m_partArray) {
        for (size_t syst = 0; syst < nSyst; ++syst) {
            for (auto idx : plist[syst]) {
                m_bitArray[key][idx] += 1 << syst;
            }
        }
    }
}

void Particle::setup_map(int name)
{
    m_partArray[name] = PartList(nSyst);
    m_partList[name] = nullptr;
    m_bitArray[name] = std::vector<size_t>();
}
