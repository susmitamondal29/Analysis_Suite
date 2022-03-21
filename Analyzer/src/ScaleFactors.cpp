#include "analysis_suite/Analyzer/interface/ScaleFactors.h"
#include "analysis_suite/Analyzer/interface/CommonEnums.h"
#include "analysis_suite/Analyzer/interface/PrescaleProvider.h"

#include <sstream>


void ScaleFactors::init(bool isMC_, TTreeReader& fReader)
{
    isMC = isMC_;
    if (isMC && fReader.GetTree()->GetBranchStatus("LHEScaleWeight"))
        LHEScaleWeight.setup(fReader, "LHEScaleWeight");
    else if (!isMC) {
        prescaler = new PrescaleProvider(scaleDir_ + "/prescale/triggerData" + yearMap.at(year_));
        std::ifstream golden_json_file(scaleDir_ + "/golden_json/golden_json_" + yearMap.at(year_) + ".json");
        golden_json_file >> golden_json;
    }
    setSF<TH1D>("pileupSF", Systematic::Pileup, "", true);
}

void ScaleFactors::setup_prescale()
{
    std::ifstream prescale_json_file(scaleDir_ + "/prescale/prescales_" + yearMap.at(year_) + ".json");
    prescale_json_file >> prescale_json;
    for (size_t i = 0; i < prescale_json["trigs"].size(); ++i) {
        trigger_idx[prescale_json["trigs"][i]] = i;
    }

    for (auto& [run, info]: prescale_json.items()) {
        if (run == "trigs") continue;
        std::istringstream iss(run);
        size_t run_num;
        iss >> run_num;

        auto lumis = info["lumi"].get<std::vector<size_t>>();
        std::vector<std::vector<size_t>> ps_info;
        for (auto& val: lumis) {
            ps_info.push_back(info[std::to_string(val)].get<std::vector<size_t>>());
        }
        prescale_info[run_num] = {lumis, ps_info};
    }
}

size_t ScaleFactors::getPScale(size_t run, size_t lumi, std::string trig)
{
    auto run_info = prescale_info[run];
    size_t lumi_idx = run_info.distance(lumi) - 1;

    return run_info.prescales[lumi_idx][trigger_idx[trig]];
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

    if (LHEScaleWeight.size() != 9) {
        return 1.;
    }
    if (isMC) {
        int varIdx = 4;
        if (currentSyst == Systematic::LHE_muF) {
            varIdx = (currentVar == eVar::Up) ? 5 : 3;

        } else if (currentSyst == Systematic::LHE_muR) {
            varIdx = (currentVar == eVar::Up) ? 7 : 1;
        }
        return LHEScaleWeight.at(varIdx);
    }
    return 1.;
}

float ScaleFactors::getPrescale(std::unordered_map<std::string, std::string>& l1_map,
                                std::vector<std::string> hlts, UInt_t run, UInt_t lumi)
{
    // std::cout << run << " " << lumi <<  std::endl;
    int ps_factor = -1;
    for (auto hlt : hlts) {
        int l1factor = prescaler->l1Prescale(l1_map[hlt], run, lumi);
        int hltfactor = prescaler->hltPrescale(hlt+"_v", run, lumi);
        // std::cout << hlt << " "<< l1_map[hlt] << " " << l1factor << " " << hltfactor << std::endl;
        if (ps_factor < 0) {
            ps_factor = hltfactor*l1factor;
        } else if(hltfactor > 0) {
            ps_factor = std::min(ps_factor, hltfactor*l1factor);
        }
    }
    // std::cout << ps_factor <<  "-------" << std::endl;
    if (ps_factor > 0) {
        return ps_factor;
    }


    return 1.;
}

int ScaleFactors::getIndPrescale(std::string hlt, std::string l1, UInt_t run, UInt_t lumi)
{
    if (isMC)
        return 1;
    int l1factor = prescaler->l1Prescale(l1, run, lumi);
    int hltfactor = prescaler->hltPrescale(hlt+"_v", run, lumi);
    if (l1factor < 0 || hltfactor < 0) {
        return -1;
    }
    return hltfactor*l1factor;
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
