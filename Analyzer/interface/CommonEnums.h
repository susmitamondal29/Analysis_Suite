#ifndef __COMMONENUMS_H_
#define __COMMONENUMS_H_

enum class Year {
    yr2016,
    yr2017,
    yr2018
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

#endif // __COMMONENUMS_H_
