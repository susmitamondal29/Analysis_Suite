#ifndef __JET_H_
#define __JET_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"


class Jet : public Particle {
    public:
        void setup(TTreeReader& fReader, int year);
        void createLooseList();
        void createBJetList();
        void createTightList();
        float getHT(std::vector<size_t> jet_list);
        float getCentrality(std::vector<size_t> jet_list);

        void setupJet() {
            createLooseList();
            createBJetList();
            createTightList();
        }

        void clear() {
            looseList.clear();
            bjetList.clear();
            tightList.clear();
            closeJetDr_by_index.clear();
        }

        std::vector<size_t> looseList;
        std::vector<size_t> bjetList;
        std::vector<size_t> tightList;
        std::unordered_map<size_t, size_t> closeJetDr_by_index;
        
        TTRArray<Int_t>* jetId;
        TTRArray<Int_t>* hadronFlavour;
        TTRArray<Float_t>* btag;

    
    private:
        float loose_bjet_cut, medium_bjet_cut, tight_bjet_cut;
        int looseId = 0b11;
};

#endif // __JET_H_
