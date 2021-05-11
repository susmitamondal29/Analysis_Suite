#ifndef __PARTICLE_H_
#define __PARTICLE_H_

#include "DataFormats/Math/interface/LorentzVector.h"
#include <TTreeReader.h>
#include <TTreeReaderArray.h>
#include <TTreeReaderValue.h>

#include <vector>

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>>
    LorentzVector;
typedef std::vector<std::vector<size_t>> PartList;

template <class T>
using TTRArray = TTreeReaderArray<T>;

class ParticleOut;
class BJetOut;
class TopOut;

class Particle {
public:
    Particle();
    virtual ~Particle(){};
    void setup(std::string name, TTreeReader& fReader, int year);
    virtual void setGoodParticles(size_t syst);

    size_t size() { return (m_pt) ? m_pt->GetSize() : 0; }
    Float_t pt(size_t idx) { return m_pt->At(idx); }
    Float_t eta(size_t idx) { return m_eta->At(idx); }
    Float_t phi(size_t idx) { return m_phi->At(idx); }
    Float_t mass(size_t idx) { return m_mass->At(idx); }

    std::vector<size_t>* list(int name) { return m_partList[name]; };
    std::vector<size_t> list(int name, size_t syst) { return m_partArray[name][syst]; };
    
    virtual void clear();

    static size_t nSyst;
    int year_;

protected:
    TTRArray<Float_t>* m_pt;
    TTRArray<Float_t>* m_eta;
    TTRArray<Float_t>* m_phi;
    TTRArray<Float_t>* m_mass;

    std::unordered_map<int, std::vector<size_t>*> m_partList;
    std::unordered_map<int, PartList> m_partArray;
};

#endif // __PARTICLE_H_
