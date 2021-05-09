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
    virtual void setGoodParticles(size_t syst){};

    template <class T>
    void fillParticle(PartList& fillArray, T& fillObject, std::vector<Int_t>& bitMap);
    template <class T>
    void fillParticle(PartList& fillArray, T& fillObject);

    TTRArray<Float_t>* pt;
    TTRArray<Float_t>* eta;
    TTRArray<Float_t>* phi;
    TTRArray<Float_t>* mass;

    static size_t nSyst;
    int year_;
};

template <class T>
void Particle::fillParticle(PartList& fillArray, T& fillObject, std::vector<Int_t>& bitMap)
{
    for (size_t syst = 0; syst < nSyst; ++syst) {
        for (auto idx : fillArray[syst]) {
            bitMap[idx] += 1 << syst;
        }
    }
    for (size_t idx = 0; idx < pt->GetSize(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.pt.push_back(pt->At(idx));
            fillObject.eta.push_back(eta->At(idx));
            fillObject.phi.push_back(phi->At(idx));
            fillObject.mass.push_back(mass->At(idx));
        }
    }
    fillObject.syst_bitMap = bitMap;
    fillObject.syst_bitMap.erase(remove(fillObject.syst_bitMap.begin(),
                                     fillObject.syst_bitMap.end(), 0),
        fillObject.syst_bitMap.end());
}

template <class T>
void Particle::fillParticle(PartList& fillArray, T& fillObject)
{
    std::vector<Int_t> bitMap(pt->GetSize());
    fillParticle(fillArray, fillObject, bitMap);
}

#endif // __PARTICLE_H_
