#ifndef __COMMONENUMS_H_
#define __COMMONENUMS_H_

#include <unordered_map>
#include <vector>

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
};

enum class Systematic {
    Nominal,
    LHEReweight,
};

enum class Variation {
    Nominal,
    Up,
    Down,
};

static const std::unordered_map<std::string, Systematic> syst_by_name = {
    { "LHEReweight", Systematic::LHEReweight },
};

static const std::unordered_map<Systematic, std::vector<Variation>> var_by_syst = {
    { Systematic::Nominal, { Variation::Nominal } },
    { Systematic::LHEReweight, { Variation::Up, Variation::Down } },
};

#endif // __COMMONENUMS_H_
