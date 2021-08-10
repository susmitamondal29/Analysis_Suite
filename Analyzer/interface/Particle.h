#ifndef __PARTICLE_H_
#define __PARTICLE_H_

#include "DataFormats/Math/interface/LorentzVector.h"
#include "analysis_suite/Analyzer/interface/Systematic.h"

#include <TTreeReader.h>
#include <TTreeReaderArray.h>
#include <TTreeReaderValue.h>

#include <vector>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>> LorentzVector;
typedef std::vector<std::vector<size_t>> PartList;

template <class T>
using TTRArray = TTreeReaderArray<T>;

class Particle : public SystematicWeights {
public:
    Particle(){};
    virtual ~Particle(){};

    void setup(std::string name, TTreeReader& fReader);
    virtual void setGoodParticles(size_t syst);

    virtual float getScaleFactor() { return 1.0; };

    size_t size() const { return (m_pt) ? m_pt->GetSize() : 0; }
    size_t size(Level level) const { return list(level).size(); }
    Float_t pt(size_t idx) const { return m_pt->At(idx); }
    Float_t eta(size_t idx) const { return m_eta->At(idx); }
    Float_t phi(size_t idx) const { return m_phi->At(idx); }
    Float_t mass(size_t idx) const { return m_mass->At(idx); }

    const std::vector<size_t>& list(Level level) const { return *m_partList.at(level); };
    const std::vector<size_t>& list(Level level, size_t syst) const { return m_partArray.at(level).at(syst); };
    const std::vector<size_t>& bitmap(Level level) const { return m_bitArray.at(level); };

    void moveLevel(Level level_start, Level level_end);
    virtual void clear();

protected:
    TTRArray<Float_t>* m_pt;
    TTRArray<Float_t>* m_eta;
    TTRArray<Float_t>* m_phi;
    TTRArray<Float_t>* m_mass;

    std::unordered_map<Level, std::vector<size_t>*> m_partList;
    std::unordered_map<Level, PartList> m_partArray;
    std::unordered_map<Level, std::vector<size_t>> m_bitArray;

    void setup_map(Level level);
    void fill_bitmap();
};

#endif // __PARTICLE_H_
