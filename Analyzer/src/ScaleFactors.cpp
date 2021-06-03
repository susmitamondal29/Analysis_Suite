#include "analysis_suite/Analyzer/interface/ScaleFactors.h"

#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include <filesystem>

ScaleFactors::ScaleFactors(Year year)
    : year_(year)
{
    std::string scaleDir = getenv("CMSSW_BASE");
    scaleDir += "/src/analysis_suite/data/scale_factors/";

    std::string strYear;
    if (year == Year::yr2016) {
        strYear = "2016";
    } else if (year == Year::yr2017) {
        strYear = "2017";
    } else {
        strYear = "2018";
    }

    TFile* f_scale_factors = new TFile((scaleDir + "event_scalefactors.root").c_str());
    f_scale_factors->cd(strYear.c_str());
    pileupSF = (TH1D*)gDirectory->Get("pileupSF");
}

float ScaleFactors::getPileupSF(int nPU)
{
    return getWeight(pileupSF, nPU);
}
