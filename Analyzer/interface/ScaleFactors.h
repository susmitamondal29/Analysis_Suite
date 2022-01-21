#ifndef __SCALEFACTORS_H_
#define __SCALEFACTORS_H_

#include <TTreeReader.h>
#include <TTreeReaderArray.h>

#include <nlohmann/json.hpp>

#include "analysis_suite/Analyzer/interface/Systematic.h"

class PrescaleProvider;

class ScaleFactors : public SystematicWeights {
public:
    ScaleFactors() {}

    void init(bool isMC_, TTreeReader& fReader);

    float getPileupSF(int nPU);

    float getLHESF();

    float getPrescale(std::unordered_map<std::string, std::string>& l1_map,
                      std::vector<std::string> hlts, UInt_t run, UInt_t lumi);

    bool inGoldenLumi(UInt_t run, UInt_t lumi);

private:

    TTreeReaderArray<Float_t>* LHEScaleWeight;

    PrescaleProvider* prescaler;

    bool isMC;

    nlohmann::json golden_json;
};

#endif // __SCALEFACTORS_H_
