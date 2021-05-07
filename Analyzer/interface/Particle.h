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

template <class T>
using TTRArray = TTreeReaderArray<T>;

class Particle {
public:
    Particle();
    virtual ~Particle(){};
    void setup(std::string name, TTreeReader& fReader, int year);
    virtual void setGoodParticles(size_t syst){};

    void fillParticle(PartList& fillList, ParticleOut& fillObject);

    TTRArray<Float_t>* pt;
    TTRArray<Float_t>* eta;
    TTRArray<Float_t>* phi;
    TTRArray<Float_t>* mass;

    static size_t nSyst;
    int year_;
};

#endif // __PARTICLE_H_
