#ifndef __PARTICLE_H_
#define __PARTICLE_H_

#include "DataFormats/Math/interface/LorentzVector.h"
#include "analysis_suite/Analyzer/interface/Systematic.h"
#include "analysis_suite/Analyzer/interface/Variable.h"

#include <TTreeReader.h>
#include <TTreeReaderArray.h>
#include <TTreeReaderValue.h>

#include <vector>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>> LorentzVector;
typedef std::vector<std::vector<size_t>> PartList;

class GenericParticle : public SystematicWeights {
public:
    GenericParticle() {};
    virtual ~GenericParticle() {};

    void setup(std::string name, TTreeReader& fReader);

    size_t size() const { return m_pt.size(); }
    size_t size(Level level) const { return list(level).size(); }
    size_t idx(Level level, size_t i) const;

    Float_t pt(size_t idx) const { return m_pt.at(idx); }
    Float_t pt(Level level, size_t i) const { return pt(idx(level, i)); }
    Float_t eta(size_t idx) const { return m_eta.at(idx); }
    Float_t eta(Level level, size_t i) const { return eta(idx(level, i)); }
    Float_t phi(size_t idx) const { return m_phi.at(idx); }
    Float_t phi(Level level, size_t i) const { return phi(idx(level, i)); }
    Float_t mass(size_t idx) const { return m_mass.at(idx); }
    Float_t mass(Level level, size_t i) const { return mass(idx(level, i)); }

    const std::vector<size_t>& list(Level level) const { return *m_partList.at(level); };
    virtual void clear();

protected:
    TRArray<Float_t> m_pt;
    TRArray<Float_t> m_eta;
    TRArray<Float_t> m_phi;
    TRArray<Float_t> m_mass;

    std::unordered_map<Level, std::vector<size_t>*> m_partList;

    virtual void setup_map(Level level);
};

class Particle : public GenericParticle {
public:
    Particle(){};
    virtual ~Particle(){};

    virtual void setupGoodLists() {std::cout << "SHOULDN'T BE CALLED" << std::endl;}
    virtual void setupGoodLists(Particle&) {std::cout << "SHOULDN'T BE CALLED (with jet)" << std::endl;}

    template <class... Args>
    void setGoodParticles(size_t syst, Args&&... args);

    virtual float getScaleFactor() { return 1.0; };
    using GenericParticle::list; // Need to have since overloading func in derived class
    const std::vector<size_t>& list(Level level, size_t syst) const { return m_partArray.at(level).at(syst); };
    const std::vector<size_t>& bitmap(Level level) const { return m_bitArray.at(level); };

    void moveLevel(Level level_start, Level level_end);

    virtual void clear() override;

protected:
    std::unordered_map<Level, PartList> m_partArray;
    std::unordered_map<Level, std::vector<size_t>> m_bitArray;

    virtual void setup_map(Level level) override;
};

template <class... Args>
void Particle::setGoodParticles(size_t syst, Args&&... args)
{
    // Setup variables
    for (auto& [key, plist] : m_partArray) {
        m_partList[key] = &plist[syst];
        m_bitArray[key].assign(size(), 0);
    }

    // Virutal class specific list making
    setupGoodLists(std::forward<Args>(args)...);

    // Fill the bitmap
    for (const auto& [key, plist] : m_partArray) {
        for (size_t syst = 0; syst < nSyst; ++syst) {
            for (auto idx : plist[syst]) {
                m_bitArray[key][idx] += 1 << syst;
            }
        }
    }
}


#endif // __PARTICLE_H_
