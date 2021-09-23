#ifndef __JET_H_
#define __JET_H_

#include <unordered_map>

#include "analysis_suite/Analyzer/interface/Particle.h"

#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

struct Btag_Info {
    BTagEntry::JetFlavor flavor_type;
    std::string jet_type;
};

class Jet : public Particle {
public:
    void setup(TTreeReader& fReader, bool isMC);

    virtual float getScaleFactor() override;

    float rawPt(size_t idx) const { return (1-rawFactor->At(idx))*pt(idx); }

    float getHT(Level level, size_t syst) { return getHT(list(level, syst)); };
    float getHT(Level level) { return getHT(list(level)); };

    float getCentrality(Level level, size_t syst) { return getCentrality(list(level, syst)); };
    float getCentrality(Level level) { return getCentrality(list(level)); };

    virtual void setupGoodLists() override
    {
        n_loose_bjet.push_back(0);
        n_medium_bjet.push_back(0);
        n_tight_bjet.push_back(0);

        createLooseList();
        createBJetList();
        createTightList();
    }

    virtual void clear() override
    {
        Particle::clear();
        closeJetDr_by_index.clear();
        n_loose_bjet.clear();
        n_medium_bjet.clear();
        n_tight_bjet.clear();
    }

    std::unordered_map<size_t, size_t> closeJetDr_by_index;

    std::vector<Int_t> n_loose_bjet, n_medium_bjet, n_tight_bjet;

    TTRArray<Int_t>* jetId;
    TTRArray<Int_t>* hadronFlavour;
    TTRArray<Float_t>* btag;
    TTRArray<Int_t>* genJetIdx;
    TTRArray<Float_t>* area;
    TTRArray<Float_t>* rawFactor;

private:
    float loose_bjet_cut, medium_bjet_cut, tight_bjet_cut;
    int looseId = 0b11;

    void createLooseList();
    void createBJetList();
    void createTightList();

    float getHT(const std::vector<size_t>& jet_list);
    float getCentrality(const std::vector<size_t>& jet_list);

    std::unordered_map<int, Btag_Info> btagInfo_by_flav = {
        {static_cast<int>(PID::Bottom), {BTagEntry::FLAV_B, "btagEff_b"}},
        {static_cast<int>(PID::Charm), {BTagEntry::FLAV_C, "btagEff_c"}},
        {static_cast<int>(PID::Jet), {BTagEntry::FLAV_UDSG, "btagEff_udsg"}},
    };

    const std::unordered_map<Systematic, std::string> systName_by_syst = {
        { Systematic::BJet_Shape_hf, "hf" },
        { Systematic::BJet_Shape_hfstats1, "hfstats1" },
        { Systematic::BJet_Shape_hfstats2, "hfstats2" },
        { Systematic::BJet_Shape_lf, "lf" },
        { Systematic::BJet_Shape_lfstats1, "lfstats1" },
        { Systematic::BJet_Shape_lfstats2, "lfstats2" },
        { Systematic::BJet_Shape_cferr1, "cferr1" },
        { Systematic::BJet_Shape_cferr2, "cferr2" },
    };

    const std::vector<Systematic> charm_systs = {
        Systematic::BJet_Shape_cferr1,
        Systematic::BJet_Shape_cferr2,
    };

    std::unordered_map<Year, std::string> btag_file = {
        {Year::yr2016, "2016Legacy_V1"},
        {Year::yr2017, "94XSF_V5_B_F"},
        {Year::yr2018, "102XSF_V2"},
    };

    void createBtagReaders();
    float getTotalBTagWeight();
    float getTotalShapeWeight();

    bool use_shape_btag = false;
    BTagCalibration calib;
    BTagCalibrationReader* btag_reader, *shape_btag_reader;

    double getBWeight(BTagEntry::JetFlavor flav, size_t idx)
    {
        std::string measType = "central";
        if (currentSyst == Systematic::BJet_BTagging) {
            measType = varName_by_var.at(currentVar);
        }
        return btag_reader->eval_auto_bounds(measType, flav, eta(idx), pt(idx));
    }
    double getShapeWeight(BTagEntry::JetFlavor flav, size_t idx) {
        std::string measType = "central";
        if (systName_by_syst.find(currentSyst) != systName_by_syst.end()) {
            measType = varName_by_var.at(currentVar) + "_" + systName_by_syst.at(currentSyst);
        }
        return btag_reader->eval_auto_bounds(measType, flav, eta(idx), pt(idx), btag->At(idx));
    }
};

#endif // __JET_H_
