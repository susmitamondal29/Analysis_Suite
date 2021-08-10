#ifndef __SCALEFACTORS_H_
#define __SCALEFACTORS_H_

#include <TTreeReader.h>
#include <TTreeReaderArray.h>

#include "analysis_suite/Analyzer/interface/Systematic.h"

class ScaleFactors : public SystematicWeights {
public:
    ScaleFactors() {}

    void init(bool isMC_, TTreeReader& fReader);

    float getPileupSF(int nPU);

    float getLHESF();

private:

    TTreeReaderArray<Float_t>* LHEScaleWeight;

    bool isMC;
};

#endif // __SCALEFACTORS_H_
