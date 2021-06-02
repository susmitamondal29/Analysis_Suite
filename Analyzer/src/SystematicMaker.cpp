#include "analysis_suite/Analyzer/interface/SystematicMaker.h"

#include "analysis_suite/Analyzer/interface/BaseSelector.h"

SystematicMaker::SystematicMaker(BaseSelector* analysis, Year year)
    : analysis_(analysis)
    , year_(year)
{
}

void SystematicMaker::applySystematic(Systematic syst, Variation var)
{
    if (syst == Systematic::LHEReweight) {
        LHEReweight(var);
    } else {
        return;
    }
}

void SystematicMaker::LHEReweight(Variation var)
{
    // [0] is muR=0.5 muF=0.5 ; [1] is muR=0.5 muF=1.0 ; [2] is muR=0.5 muF=2.0 ;
    // [3] is muR=0.1 muF=0.5 ; [4] is muR=1.0 muF=1.0 ; [5] is muR=1.0 muF=2.0 ;
    // [6] is muR=2.0 muF=0.5 ; [7] is muR=2.0 muF=1.0 ; [8] is muR=2.0 muF=2.0 ;
    int varIdx = 4;
    if (var == Variation::Up) {
        varIdx = 5;
    } else if (var == Variation::Down) {
        varIdx = 3;
    }
    (*analysis_->weight) *= analysis_->LHEScaleWeight->At(varIdx);
}
