#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

#include <math.h>

float mt_f(float pt1, float pt2, float phi1, float phi2)
{
    return sqrt(2*pt1*pt2*(1-cos(phi1 - phi2)));
}

float deltaPhi(float phi1, float phi2)
{
    float dphi = phi1 - phi2;
    if ( dphi > M_PI )
        dphi -= 2.0*M_PI;
    else if ( dphi <= -M_PI ) {
        dphi += 2.0*M_PI;
    }
    return dphi;
}

float deltaR(float eta1, float eta2, float phi1, float phi2)
{
    return pow(eta1-eta2, 2) + pow(deltaPhi(phi1, phi2), 2);
}
