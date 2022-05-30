#ifndef SYSTEMATIC_H_
#define SYSTEMATIC_H_

#include <TH1.h>
#include <TH2.h>
#include <TFile.h>
#include <memory>
#include <variant>

#include "correction.h"

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

typedef std::vector<correction::Variable::Type> WeightVector;

struct WeightHolder {
    correction::Correction::Ref scale_;
    Systematic syst_;
    std::unordered_map<eVar, std::string> name_by_var;

    WeightHolder() {}

    WeightHolder(correction::Correction::Ref scale) : scale_(scale) {}

    WeightHolder(correction::Correction::Ref scale, Systematic syst, std::vector<std::string> varNames)
        : scale_(scale)
        , syst_(syst)
    {
        name_by_var[eVar::Nominal] = varNames.at(0);
        name_by_var[eVar::Up] = varNames.at(1);
        name_by_var[eVar::Down] = varNames.at(2);
    }

    std::string systName(Systematic syst, eVar var) {
        if (syst_ != syst) return name_by_var[eVar::Nominal];
        else return name_by_var[var];
    }

    float evaluate(WeightVector vec) { return scale_->evaluate(vec); };
};

class SystematicWeights {
public:
    static size_t nSyst;
    static TFile* f_scale_factors;
    static Year year_;
    static std::string scaleDir_;
    static eVar currentVar;
    static Systematic currentSyst;

protected:
    auto getScaleFile(std::string group, std::string filename)
    {
        std::string scale_file = scaleDir_ + "/POG/" + group;
        scale_file += "/" + yearMap.at(year_) + "_UL";
        scale_file += "/" + filename + ".json.gz";
        return correction::CorrectionSet::from_file(scale_file.c_str());
    }

    std::string systName(WeightHolder& weight) { return weight.systName(currentSyst, currentVar); }

    // template <class... Args>
    // float getWeight(std::string name, Args... args)
    // {
    //     return scales_by_name[name]->getWeight(currentSyst, currentVar, args...);
    // }
};

#endif // SYSTEMATIC_H_
