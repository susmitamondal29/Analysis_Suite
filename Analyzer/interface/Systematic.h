#ifndef SYSTEMATIC_H_
#define SYSTEMATIC_H_

#include <TH1.h>
#include <TH2.h>
#include <TFile.h>

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

struct WeightGetter {
    TH1* hist;
    Systematic syst;
    TH1* up = nullptr;
    TH1* down = nullptr;

    template <class... Args>
    float getWeight(Systematic syst_, eVar var_, Args... args)
    {
        if(syst_ != syst) {
            return getBinContent(hist, args...);
        } else if(var_ == eVar::Up) {
            if (up)
                return getBinContent(up, args...);
            else
                return getBinContent(hist, args...) + getBinError(hist, args...);
        } else if (var_ == eVar::Down) {
            if (down)
                return getBinContent(down, args...);
            else
                return getBinContent(hist, args...) - getBinError(hist, args...);
        }
        return 0.;
    }

    template <class... Args>
    float getBinContent(TH1* h, Args... args) { return h->GetBinContent(h->FindBin(args...)); }

    template <class... Args>
    float getBinError(TH1* h, Args... args) { return h->GetBinError(h->FindBin(args...)); }
};

class SystematicWeights {
public:
    static size_t nSyst;
    static TFile* f_scale_factors;
    static Year year_;
    static std::string yearStr_;
    static std::string scaleDir_;
    static eVar currentVar;
    static Systematic currentSyst;

protected:
    std::unordered_map<std::string, WeightGetter*> scales_by_name;

    template <class T>
    void setSF(std::string name, Systematic syst, std::string map_name="", bool separateErrors=false)
    {
        if (map_name.empty())
            map_name = name;
        std::string histname = yearStr_ + "/" + name;
        if (separateErrors) {
            scales_by_name[map_name] = new WeightGetter({static_cast<T*>(f_scale_factors->Get(histname.c_str())), syst});
        } else {
            scales_by_name[map_name] = new WeightGetter({static_cast<T*>(f_scale_factors->Get(histname.c_str())), syst,
                    static_cast<T*>(f_scale_factors->Get((histname+"_up").c_str())),
                    static_cast<T*>(f_scale_factors->Get((histname+"_down").c_str()))});
        }
    }

    template <class... Args>
    float getWeight(std::string name, Args... args)
    {
        return scales_by_name[name]->getWeight(currentSyst, currentVar, args...);
    }
};

#endif // SYSTEMATIC_H_
