#ifndef COMMONFUNCS_H_
#define COMMONFUNCS_H_

#include <unordered_map>
#include <cmath>

template <class A, class B>
A get_by_val(std::unordered_map<A, B> map, B val_) {
    for (auto& [key, val] : map) {
        if (val == val_)
            return key;
    }
    throw std::out_of_range("Could not find value in map");
}

float mt_f(float pt1, float pt2, float phi1, float phi2);

#endif // COMMONFUNCS_H_
