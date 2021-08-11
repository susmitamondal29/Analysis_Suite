#include "analysis_suite/Analyzer/interface/Systematic.h"


size_t SystematicWeights::nSyst = 0;
Year SystematicWeights::year_ = Year::yrDefault;
std::string SystematicWeights::yearStr_ = "";
std::string SystematicWeights::scaleDir_ = "";
TFile* SystematicWeights::f_scale_factors = nullptr;
Variation SystematicWeights::currentVar = Variation::Nominal;
Systematic SystematicWeights::currentSyst = Systematic::Nominal;
