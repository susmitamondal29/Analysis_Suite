#ifndef __SCALEFACTORS_H_
#define __SCALEFACTORS_H_

#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

#include "TH1.h"
#include "TH2.h"
#include "TFile.h"

#include <vector>
#include <functional>

#include "analysis_suite/Analyzer/interface/ResolvedTop.h"
#include "analysis_suite/Analyzer/interface/Jet.h"
#include "analysis_suite/Analyzer/interface/GenParticle.h"
#include "analysis_suite/Analyzer/interface/Lepton.h"

class ScaleFactors {
public:
    ScaleFactors() {}
    ScaleFactors(int year);

    float getBJetSF(Jet& jets);
    float getPileupSF(int nPU);
        float getResolvedTopSF(ResolvedTop& top, GenParticle& genPart);
        
        float getElectronSF(Lepton& elec);
        float getMuonSF(Lepton& muon);

    private:
        int year_;
        BTagCalibration calib;
        BTagCalibrationReader btag_reader;

        TH2D *h_btag_eff_b, *h_btag_eff_c, *h_btag_eff_udsg;
        TH1F *topSF, *fakeTopSF;
        TH1D *pileupSF;
        TH2F *electronLowSF, *electronSF, *electronSusySF;
        TH2D* muonSF;

        template <typename T>
        float getWeight(T* hist, float val) {
            return hist->GetBinContent(hist->FindBin(val));
        }

        template <typename T>
        float getWeight(T* hist, float val1, float val2) {
            return hist->GetBinContent(hist->FindBin(val1, val2));
        }

        template <typename T>
        float getWeightPtAbsEta(T* hist, float pt, float eta) {
            return hist->GetBinContent(hist->FindBin(pt, fabs(eta)));
        }

        float elecPtMax = 500-0.1;
        float muonPtMax = 120-0.1;
        float muonPtMin = 20.;
};

#endif // __SCALEFACTORS_H_
