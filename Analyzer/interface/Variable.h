#ifndef VARIABLE_H_
#define VARIABLE_H_

#include <TTreeReader.h>
#include <TTreeReaderArray.h>
#include <TTreeReaderValue.h>

#include "analysis_suite/Analyzer/interface/logging.h"

template <class T>
class TRVariable {
public:
    TRVariable() {}

    TRVariable(TTreeReader& fReader, std::string branch) {
        setup(fReader, branch);
    }

    void setup(TTreeReader& fReader, std::string branch) {
        if (fReader.GetTree()->GetBranchStatus(branch.c_str())) {
            val = new TTreeReaderValue<T>(fReader, branch.c_str());
        } else {
            std::cout << "Branch (" << branch << ") not found, will continue to run" << std::endl;
        }
    }
    T operator*() const {
        if (val) {
            return **val;
        } else if (std::is_same<T, bool>::value) {
            return false;
        } else {
            return 0.;
        }
    }
private:
    TTreeReaderValue<T>* val = nullptr;
};



template <class T>
class TRArray {

public:
    TRArray() {}

    TRArray(TTreeReader& fReader, std::string branch) {
        setup(fReader, branch);
    }

    void setup(TTreeReader& fReader, std::string branch) {
        if (fReader.GetTree()->GetBranchStatus(branch.c_str())) {
            array = new TTreeReaderArray<T>(fReader, branch.c_str());
        } else {
            std::cout << "Branch (" << branch << ") not found, will continue to run" << std::endl;
        }
    }
    T at(size_t idx) const {
        if (array) {
            return array->At(idx);
        } else if (std::is_same<T, bool>::value) {
            return false;
        } else {
            return 0.;
        }
    }
    size_t size() const {
        if (array) {
            return array->GetSize();
        } else {
            return 0;
        }
    }
    auto begin() {
        return array->begin();
    }
    auto end() {
        return array->end();
    }
private:
    TTreeReaderArray<T>* array = nullptr;
};




#endif // VARIABLE_H_
