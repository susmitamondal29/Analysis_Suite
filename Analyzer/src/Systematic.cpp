#include "analysis_suite/Analyzer/interface/Systematic.h"


size_t SystematicWeights::nSyst = 0;
Year SystematicWeights::year_ = Year::yrDefault;
std::string SystematicWeights::scaleDir_ = "";
eVar SystematicWeights::currentVar = eVar::Nominal;
Systematic SystematicWeights::currentSyst = Systematic::Nominal;
