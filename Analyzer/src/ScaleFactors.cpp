#include "analysis_suite/Analyzer/interface/ScaleFactors.h"

void ScaleFactors::init(bool isMC_, TTreeReader& fReader)
{
    isMC = isMC_;
    if (isMC)
        LHEScaleWeight = new TTreeReaderArray<Float_t>(fReader, "LHEScaleWeight");

    setSF<TH1D>("pileupSF", Systematic::Pileup, "", true);
}

float ScaleFactors::getPileupSF(int nPU)
{
    return getWeight("pileupSF", nPU);
}

float ScaleFactors::getLHESF()
{
    // [0] is muR=0.5 muF=0.5 ; [1] is muR=0.5 muF=1.0 ; [2] is muR=0.5 muF=2.0 ;
    // [3] is muR=0.1 muF=0.5 ; [4] is muR=1.0 muF=1.0 ; [5] is muR=1.0 muF=2.0 ;
    // [6] is muR=2.0 muF=0.5 ; [7] is muR=2.0 muF=1.0 ; [8] is muR=2.0 muF=2.0 ;

    if (LHEScaleWeight->GetSize() != 9) {
        return 1.;
    }
    if (isMC) {
        int varIdx = 4;
        if (currentSyst == Systematic::LHE_muF) {
            varIdx = (currentVar == eVar::Up) ? 5 : 3;

        } else if (currentSyst == Systematic::LHE_muR) {
            varIdx = (currentVar == eVar::Up) ? 7 : 1;
        }
        return LHEScaleWeight->At(varIdx);
    }
    return 1.;
}
