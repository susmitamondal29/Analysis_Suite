#ifndef __JET_H_
#define __JET_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

class Jet : public Particle {
public:
    void setup(TTreeReader& fReader);

    virtual float getScaleFactor() override;

    float getHT(Level level, size_t syst) { return getHT(list(level, syst)); };
    float getHT(Level level) { return getHT(list(level)); };

    float getCentrality(Level level, size_t syst) { return getCentrality(list(level, syst)); };
    float getCentrality(Level level) { return getCentrality(list(level)); };

    virtual void setGoodParticles(size_t syst) override
    {
        currentVar = Variation::Nominal;
        Particle::setGoodParticles(syst);
        n_loose_bjet.push_back(0);
        n_medium_bjet.push_back(0);
        n_tight_bjet.push_back(0);

        createLooseList();
        createBJetList();
        createTightList();

        fill_bitmap();
    }

    virtual void clear() override
    {
        Particle::clear();
        closeJetDr_by_index.clear();
        n_loose_bjet.clear();
        n_medium_bjet.clear();
        n_tight_bjet.clear();
    }

    Variation currentVar = Variation::Nominal;

    std::unordered_map<size_t, size_t> closeJetDr_by_index;

    std::vector<Int_t> n_loose_bjet, n_medium_bjet, n_tight_bjet;

    TTRArray<Int_t>* jetId;
    TTRArray<Int_t>* hadronFlavour;
    TTRArray<Float_t>* btag;

private:
    float loose_bjet_cut, medium_bjet_cut, tight_bjet_cut;
    int looseId = 0b11;

    void createLooseList();
    void createBJetList();
    void createTightList();

    float getHT(const std::vector<size_t>& jet_list);
    float getCentrality(const std::vector<size_t>& jet_list);

    TH2D *btagEff_b, *btagEff_c, *btagEff_udsg;
    BTagCalibration calib;
    std::unordered_map<Variation, BTagCalibrationReader*> bReader_by_var;
    const std::unordered_map<Variation, std::string> varName_by_var = {
        { Variation::Nominal, "central" },
        { Variation::Up, "up" },
        { Variation::Down, "down" },
    };

    void createBtagReader(Variation var)
    {
        BTagCalibrationReader* btag_reader = new BTagCalibrationReader(BTagEntry::OP_MEDIUM, varName_by_var.at(var));
        btag_reader->load(calib, BTagEntry::FLAV_B, "comb");
        btag_reader->load(calib, BTagEntry::FLAV_C, "comb");
        btag_reader->load(calib, BTagEntry::FLAV_UDSG, "incl");
        bReader_by_var[var] = btag_reader;
    }

    double getBWeight(BTagEntry::JetFlavor flav, size_t idx)
    {
        return bReader_by_var.at(currentVar)->eval_auto_bounds(varName_by_var.at(currentVar), flav, eta(idx), pt(idx));
    }
};

#endif // __JET_H_
