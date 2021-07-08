#ifndef SYSTEMATICS_H_
#define SYSTEMATICS_H_

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

#include <vector>

class BaseSelector;

class SystematicMaker {
public:
    SystematicMaker(BaseSelector* analysis, Year year);
    void applySystematic(Systematic syst, Variation var);

private:
    BaseSelector* analysis_;
    Year year_;
    bool isMC;
};

#endif // SYSTEMATICS_H_
