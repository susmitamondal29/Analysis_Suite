#ifndef COMMONFUNCS_H_
#define COMMONFUNCS_H_

template <class A, class B>
A get_by_val(std::unordered_map<A, B> map, B val_) {
    for (auto& [key, val] : map) {
        if (val == val_)
            return key;
    }
    throw std::out_of_range("Could not find value in map");
}




#endif // COMMONFUNCS_H_
