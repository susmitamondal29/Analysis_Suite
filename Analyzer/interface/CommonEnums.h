#ifndef __COMMONENUMS_H_
#define __COMMONENUMS_H_

#include <unordered_map>
#include <vector>

const size_t MAX_PARTICLES = 65535;

enum class Year {
    yr2016,
    yr2017,
    yr2018,
    yrDefault,
};

static const std::unordered_map<std::string, Year> yearMap = {
    { "2016", Year::yr2016 },
    { "2017", Year::yr2017 },
    { "2018", Year::yr2018 }
};

enum class PID {
    Muon = 13,
    Electron = 11,
    Top = 6,
    Bottom = 5,
    Charm = 4,
    Jet
};

enum class Level {
    Loose,
    Fake,
    Tight,
    Top,
    Bottom,
    Jet,
};

enum class Systematic {
    Nominal,
    LHE_muF,
    LHE_muR,
    BJet_BTagging,
    BJet_Eff,
    Muon_ID,
    Muon_Iso,
    Electron_SF,
    Electron_Susy,
    Top_SF,
    Pileup,
    Jet_JER,
    Jet_JES,
};

enum class eVar {
    Nominal,
    Up,
    Down,
};

static const std::unordered_map<std::string, Systematic> syst_by_name = {
    { "LHE_muF", Systematic::LHE_muF },
    { "LHE_muR", Systematic::LHE_muR },
    { "BJet_BTagging", Systematic::BJet_BTagging },
    { "BJet_Eff", Systematic::BJet_Eff },
    { "Muon_ID", Systematic::Muon_ID },
    { "Muon_Iso", Systematic::Muon_Iso },
    { "Electron_SF", Systematic::Electron_SF },
    { "Electron_Susy", Systematic::Electron_Susy },
    { "Top_SF", Systematic::Top_SF },
    { "Pileup", Systematic::Pileup },
    { "Jet_JER", Systematic::Jet_JER },
    { "Jet_JES", Systematic::Jet_JES },
};

static const std::unordered_map<Systematic, std::vector<eVar>> var_by_syst = {
    { Systematic::Nominal, { eVar::Nominal } },
    { Systematic::LHE_muF, { eVar::Up, eVar::Down } },
    { Systematic::LHE_muR, { eVar::Up, eVar::Down } },
    { Systematic::BJet_BTagging, { eVar::Up, eVar::Down } },
    { Systematic::BJet_Eff, { eVar::Up, eVar::Down } },
    { Systematic::Muon_ID, { eVar::Up, eVar::Down } },
    { Systematic::Muon_Iso, { eVar::Up, eVar::Down } },
    { Systematic::Electron_SF, { eVar::Up, eVar::Down } },
    { Systematic::Electron_Susy, { eVar::Up, eVar::Down } },
    { Systematic::Top_SF, { eVar::Up, eVar::Down } },
    { Systematic::Pileup, { eVar::Up, eVar::Down } },
    { Systematic::Jet_JER, { eVar::Up, eVar::Down } },
    { Systematic::Jet_JES, { eVar::Up, eVar::Down } },
};

#endif // __COMMONENUMS_H_
