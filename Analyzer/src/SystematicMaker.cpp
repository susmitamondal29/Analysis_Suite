#include "analysis_suite/Analyzer/interface/SystematicMaker.h"

#include "analysis_suite/Analyzer/interface/BaseSelector.h"

SystematicMaker::SystematicMaker(BaseSelector* analysis, Year year)
    : analysis_(analysis)
    , year_(year)
    , isMC(analysis->isMC_)

{
}

void SystematicMaker::applySystematic(Systematic syst, Variation var)
{
    // [0] is muR=0.5 muF=0.5 ; [1] is muR=0.5 muF=1.0 ; [2] is muR=0.5 muF=2.0 ;
    // [3] is muR=0.1 muF=0.5 ; [4] is muR=1.0 muF=1.0 ; [5] is muR=1.0 muF=2.0 ;
    // [6] is muR=2.0 muF=0.5 ; [7] is muR=2.0 muF=1.0 ; [8] is muR=2.0 muF=2.0 ;
    if (isMC) {
        if (syst == Systematic::LHE_muF) {
            int varIdx = (var == Variation::Up) ? 5 : 3;
            (*analysis_->weight) *= analysis_->LHEScaleWeight->At(varIdx);
        } else if (syst == Systematic::LHE_muR) {
            int varIdx = (var == Variation::Up) ? 7 : 1;
            (*analysis_->weight) *= analysis_->LHEScaleWeight->At(varIdx);
        } else if (syst == Systematic::BTagging) {
            analysis_->jet.currentVar = var;
        } else {
            return;
        }
    } else {
        // data systematics
    }
}
