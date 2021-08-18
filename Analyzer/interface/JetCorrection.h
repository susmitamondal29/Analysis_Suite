#ifndef JETCORRECTION_H_
#define JETCORRECTION_H_

#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include "analysis_suite/Analyzer/interface/Systematic.h"

#include "JetMETCorrections/Modules/interface/JetResolution.h"
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetResolutionObject.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

#include <iostream>
#include <random>

class JetCorrection : public SystematicWeights {
public:
    JetCorrection() {};

    void setup(Year year);

    std::random_device rd{};
    std::mt19937 gen{rd()};

    JME::JetResolutionScaleFactor* res_sf;
    JME::JetResolution* resolution;
    JetCorrectionUncertainty* jecUnc;
    FactorizedJetCorrector* jecCentral;

    float getJES(float pt, float eta);
    float getJER(float pt, float eta, float rho, float genPt);


private:
    // https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECDataMC#Recommended_for_MC
    std::unordered_map<Year, std::string> jecTagsMC = {
        {Year::yr2016, "Summer16_07Aug2017_V11_MC"},
        {Year::yr2017, "Fall17_17Nov2017_V32_MC"},
        {Year::yr2018, "Autumn18_V19_MC"},
        // {Year::yr2016UL_preVFP, "Summer19UL16APV_V7_MC"},
        // {Year::yr2016UL, "Summer19UL16_V7_MC"},
        // {Year::yr2017UL, "Summer19UL17_V6_MC"},
        // {Year::yr2018UL, "Summer19UL18_V5_MC"},
    };

    // https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
    std::unordered_map<Year, std::string> jerTagsMC = {
        {Year::yr2016, "Summer16_25nsV1_MC"},
        {Year::yr2017, "Fall17_V3_MC"},
        {Year::yr2018, "Autumn18_V7b_MC"},
        // {Year::yr2016UL_preVFP, "Summer20UL16APV_JRV3_MC"},
        // {Year::yr2016UL, "Summer20UL16_JRV3_MC"},
        // {Year::yr2017UL, "Summer19UL17_JRV2_MC"},
        // {Year::yr2018UL, "Summer19UL18_JRV2_MC"},
    };


};

#endif // JETCORRECTION_H_
