#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

float mt_f(float pt1, float pt2, float phi1, float phi2)
{
    return sqrt(2*pt1*pt2*(1-cos(phi1 - phi2)));
}
