#include "analysis_suite/Analyzer/interface/ScaleFactors.h"
#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include "analysis_suite/Analyzer/interface/PrescaleProvider.h"

void ScaleFactors::init(bool isMC_, TTreeReader& fReader)
{
    isMC = isMC_;
    if (isMC && fReader.GetTree()->GetBranchStatus("LHEScaleWeight"))
        LHEScaleWeight = new TTreeReaderArray<Float_t>(fReader, "LHEScaleWeight");
    else if (!isMC) {
        prescaler = new PrescaleProvider(scaleDir_ + "/prescale/triggerData" + yearMap.at(year_));
        std::ifstream golden_json_file(scaleDir_ + "/golden_json/golden_json_" + yearMap.at(year_) + ".json");
        golden_json_file >> golden_json;
    }
    setSF<TH1D>("pileupSF", Systematic::Pileup, "", true);
}

float ScaleFactors::getPileupSF(int nPU)
{
    return getWeight("pileupSF", nPU);
}

float ScaleFactors::getLHESF()
{
    // [0] is muR=0.5 muF=0.5 ; [1] is muR=0.5 muF=1.0 ; [2] is muR=0.5 muF=2.0 ;
    // [3] is muR=0.1 muF=0.5 ; [4] is muR=1.0 muF=1.0 ; [5] is muR=1.0 muF=2.0 ;
    // [6] is muR=2.0 muF=0.5 ; [7] is muR=2.0 muF=1.0 ; [8] is muR=2.0 muF=2.0 ;

    if (LHEScaleWeight->GetSize() != 9) {
        return 1.;
    }
    if (isMC) {
        int varIdx = 4;
        if (currentSyst == Systematic::LHE_muF) {
            varIdx = (currentVar == eVar::Up) ? 5 : 3;

        } else if (currentSyst == Systematic::LHE_muR) {
            varIdx = (currentVar == eVar::Up) ? 7 : 1;
        }
        return LHEScaleWeight->At(varIdx);
    }
    return 1.;
}

float ScaleFactors::getPrescale(std::unordered_map<std::string, std::string>& l1_map,
                                std::vector<std::string> hlts, UInt_t run, UInt_t lumi)
{
    if (!isMC) {
        int ps_factor = -1;
        for (auto hlt : hlts) {
            int l1factor = prescaler->l1Prescale(l1_map[hlt], run, lumi);
            int hltfactor = prescaler->hltPrescale(hlt+"_v", run, lumi);
            if (ps_factor < 0) {
                ps_factor = hltfactor*l1factor;
            } else if(hltfactor > 0) {
                ps_factor = std::min(ps_factor, hltfactor*l1factor);
            }
        }
        if (ps_factor > 0) {
            return ps_factor;
        }
    }
    return 1.;
}

bool ScaleFactors::inGoldenLumi(UInt_t run, UInt_t lumi)
{
    if (golden_json.contains(std::to_string(run))) {
        for (auto lumi_pair : golden_json[std::to_string(run)]) {
            if (lumi < lumi_pair[0]) {
                return false;
            } else if (lumi <= lumi_pair[1]) {
                return true;
            }
        }
    }
    return false;
}
