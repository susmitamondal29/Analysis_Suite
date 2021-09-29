#include "analysis_suite/Analyzer/interface/JetCorrection.h"

#include <filesystem>
#include <stdlib.h>
#include <cmath>

void JetCorrection::setup(Year year)
{
    namespace fs = std::filesystem;
    std::string jecTag = jecTagsMC[year];
    std::string jerTag = jerTagsMC[year];
    std::string jetType = "AK4PFchs";
    fs::path jme_path = fs::path(getenv("CMSSW_BASE")) / scaleDir_ / "JEC";

    // make directory /tmp/USERNAME for putting unpacked files
    auto tmp_path = fs::temp_directory_path() / getenv("USER");
    fs::create_directory(tmp_path);

    std::stringstream tar;
    tar << "tar -C "<< tmp_path << " -xf ";
    std::system((tar.str() + (jme_path/(jerTag+".tgz")).string() + " &>/dev/null").c_str());
    std::system((tar.str() + (jme_path/(jecTag+".tgz")).string() + " &>/dev/null").c_str());


    std::vector<JetCorrectorParameters> param_vec = {
        JetCorrectorParameters(tmp_path/(jecTag + "_L1FastJet_" + jetType + ".txt")),
        JetCorrectorParameters(tmp_path/(jecTag + "_L2Relative_" + jetType + ".txt")),
        JetCorrectorParameters(tmp_path/(jecTag + "_L3Absolute_" + jetType + ".txt")),
        JetCorrectorParameters(tmp_path/(jecTag + "_L2L3Residual_" + jetType + ".txt")),
    };
    JetCorrectorParameters parameters(tmp_path/(jecTag + "_Uncertainty_" + jetType + ".txt"));

    jecCentral = new FactorizedJetCorrector(param_vec);
    jecUnc = new JetCorrectionUncertainty(parameters);
    res_sf = new JME::JetResolutionScaleFactor(tmp_path/(jerTag + "_SF_" + jetType + ".txt"));
    resolution = new JME::JetResolution(tmp_path/(jerTag + "_PtResolution_" + jetType + ".txt"));

    // Delete tmp folder
    fs::remove_all(tmp_path);
}

float JetCorrection::getJER(float pt, float eta, float rho, float genPt)
{
    float sf = 1.;
    if (currentSyst != Systematic::Jet_JES || currentVar == eVar::Nominal) {
        sf = res_sf->getScaleFactor({{JME::Binning::JetPt, pt},
                                     {JME::Binning::JetEta, eta}});
    } else if(currentVar == eVar::Up) {
        sf = res_sf->getScaleFactor({{JME::Binning::JetPt, pt}, {JME::Binning::JetEta, eta}},
                                    Variation::UP);
    } else {
        sf = res_sf->getScaleFactor({{JME::Binning::JetPt, pt}, {JME::Binning::JetEta, eta}},
                                    Variation::DOWN);
    }

    if (genPt < 0.) {
        return sf + (1-sf)*(genPt/pt);
        //return pt + (sf-1)*(pt - genPt);
    } else if(sf > 1) {
        float res = resolution->getResolution({{JME::Binning::JetPt, pt},
                                                   {JME::Binning::JetEta, eta},
                                                   {JME::Binning::Rho, rho}});
        std::normal_distribution<> gaussian{0, res};
        return 1 + gaussian(gen)*sqrt(pow(sf,2) - 1);
        //return pt + pt*gaussian(gen)*sqrt(pow(sf,2) - 1);
    }
    return 1.;
    //return pt;
}

float JetCorrection::getJES(float pt, float eta)
{
    // jecCentral->setJetPt(pt);
    // jecCentral->setJetEta(eta);
    // jecCentral->setJetA(eta);
    // jecCentral->setRho(eta);
    // float corr = jecCentral->getCorrection();
    // float jecPt = pt*corr;
    // std::cout << "correction: " << corr << std::endl;
    if (currentSyst != Systematic::Jet_JER || currentVar == eVar::Nominal) {
        return 1.;
        //return pt;
    } else {
        jecUnc->setJetPt(pt);
        jecUnc->setJetEta(eta);
        float delta = jecUnc->getUncertainty(true);
        return (currentVar == eVar::Up) ? (1+delta) : (1-delta);
        // return (currentVar == eVar::Up) ? (1+delta)*pt : (1-delta)*pt;
    }
}
