#ifndef JETCORRECTION_H_
#define JETCORRECTION_H_

#include "JetMETCorrections/Modules/interface/JetResolution.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

#include <iostream>
#include <random>

class JetCorrection {
public:
    JetCorrection(std::string factors_file, std::string filename);

    std::random_device rd{};
    std::mt19937 gen{rd()};
    JME::JetResolutionScaleFactor res_sf;
    JME::JetResolution resolution;

    JetCorrectionUncertainty* jecUnc;

    float getJER(float pt, float eta);
    float getJES(float pt, float eta, float rho, float genPt);
};

#endif // JETCORRECTION_H_
