#ifndef __SCALEFACTORS_H_
#define __SCALEFACTORS_H_

#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

#include "TFile.h"
#include "TH1.h"
#include "TH2.h"

#include <functional>
#include <vector>

#include "analysis_suite/Analyzer/interface/Jet.h"

class ScaleFactors {
public:
    ScaleFactors() {}
    ScaleFactors(Year year);

    float getBJetSF(const Jet& jets);
    float getPileupSF(int nPU);

private:
    Year year_;
    BTagCalibration calib;
    BTagCalibrationReader btag_reader;

    TH2D *h_btag_eff_b, *h_btag_eff_c, *h_btag_eff_udsg;
    TH1D* pileupSF;

    template <typename T>
    float getWeight(T* hist, float val)
    {
        return hist->GetBinContent(hist->FindBin(val));
    }

    template <typename T>
    float getWeight(T* hist, float val1, float val2)
    {
        return hist->GetBinContent(hist->FindBin(val1, val2));
    }
};

#endif // __SCALEFACTORS_H_
