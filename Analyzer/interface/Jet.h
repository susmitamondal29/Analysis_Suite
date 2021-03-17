#ifndef __JET_H_
#define __JET_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

struct BJetOut {
    std::vector<Float_t> pt;
    std::vector<Float_t> eta;
    std::vector<Float_t> phi;
    std::vector<Float_t> mass;
    std::vector<Float_t> discriminator;
    Int_t n_loose;
    Int_t n_medium;
    Int_t n_tight;
    void clear()
    {
        pt.clear();
        eta.clear();
        phi.clear();
        mass.clear();
        discriminator.clear();
    }
};

class Jet : public Particle {
public:
    void setup(TTreeReader& fReader, int year);
    void createLooseList();
    void createBJetList();
    void createTightList();
    float getHT(std::vector<size_t> jet_list);
    float getCentrality(std::vector<size_t> jet_list);
    void fillBJet(std::vector<size_t>& fillList, BJetOut& fillObject);

    void setupJet()
    {
        createLooseList();
        createBJetList();
        createTightList();
    }

    void clear()
    {
        looseList.clear();
        bjetList.clear();
        tightList.clear();
        closeJetDr_by_index.clear();
        n_loose_bjet = 0;
        n_medium_bjet = 0;
        n_tight_bjet = 0;
    }

    std::vector<size_t> looseList;
    std::vector<size_t> bjetList;
    std::vector<size_t> tightList;
    std::unordered_map<size_t, size_t> closeJetDr_by_index;
    size_t n_loose_bjet, n_medium_bjet, n_tight_bjet;

    TTRArray<Int_t>* jetId;
    TTRArray<Int_t>* hadronFlavour;
    TTRArray<Float_t>* btag;

private:
    float loose_bjet_cut, medium_bjet_cut, tight_bjet_cut;
    int looseId = 0b11;
};

#endif // __JET_H_
