#include "analysis_suite/Analyzer/interface/JetCorrection.h"

#include <cmath>

JetCorrection::JetCorrection(std::string factors_file, std::string filename)
    : res_sf(factors_file)
    , resolution(factors_file)
{
    // JetCorrectorParameters parameters(filename, "");
    // jecUnc = new JetCorrectionUncertainty(parameters);
}


float JetCorrection::getJES(float pt, float eta, float rho, float genPt)
{

    // We do the same thing to access the scale factors}
    float sf = res_sf.getScaleFactor({{JME::Binning::JetPt, pt},
                                      {JME::Binning::JetEta, eta}});

    // Access up and down variation of the scale factor
    float sf_up = res_sf.getScaleFactor({{JME::Binning::JetPt, pt}, {JME::Binning::JetEta, eta}},
                                        Variation::UP);
    float sf_down = res_sf.getScaleFactor({{JME::Binning::JetPt, pt}, {JME::Binning::JetEta, eta}},
                                          Variation::DOWN);
    std::cout << "Scale factors (Nominal / Up / Down) : " << sf << " / " << sf_up << " / " << sf_down << std::endl;

    float smear = pt;
    if (genPt != 0) {
        smear += (sf-1)*(pt - genPt);
    } else {
        float res = resolution.getResolution({{JME::Binning::JetPt, pt},
                                              {JME::Binning::JetEta, eta},
                                              {JME::Binning::Rho, rho}});
        if (res > 1) {
            std::normal_distribution<> gaussian{0, res};
            smear += gaussian(gen)*sqrt(pow(sf,2) - 1);
        }
    }
    return smear;
}

float JetCorrection::getJER(float pt, float eta)
{
    jecUnc->setJetPt(pt);
    jecUnc->setJetEta(eta);
    float delta = jecUnc->getUncertainty(true);
    //    jet_pt_jesUp = jet_pt_nom*(1+delta);
    return delta;
}
