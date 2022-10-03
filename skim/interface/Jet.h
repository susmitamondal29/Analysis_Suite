#ifndef __JET_H_
#define __JET_H_

#include <unordered_map>
#include <random>

#include "analysis_suite/skim/interface/Particle.h"

#include <complex>

enum PUID { PU_Tight = 0, PU_Medium = 1, PU_Loose = 2 };

class Jet : public Particle {
public:
    void setup(TTreeReader& fReader);

    virtual float getScaleFactor() override;
    float getTotalBTagWeight();

    float pt_(size_t idx) const override { return m_pt.at(idx)*m_jec->at(idx); }
    float nompt(size_t idx) const { return m_pt.at(idx); }
    float rawPt(size_t idx) const { return (1-rawFactor.at(idx))*m_pt.at(idx); }

    float getHT(Level level, size_t syst) { return getHT(list(level, syst)); };
    float getHT(Level level) { return getHT(list(level)); };

    float getCentrality(Level level, size_t syst) { return getCentrality(list(level, syst)); };
    float getCentrality(Level level) { return getCentrality(list(level)); };

    std::complex<float> get_momentum_change();

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

        for (auto& [syst, scales] : m_jet_scales ) {
            scales.clear();
        }
    }

    std::unordered_map<size_t, size_t> closeJetDr_by_index;

    std::vector<Int_t> n_loose_bjet, n_medium_bjet, n_tight_bjet;

    TRArray<Int_t> jetId;
    TRArray<Int_t> hadronFlavour;
    TRArray<Float_t> btag;
    TRArray<Int_t> genJetIdx;
    TRArray<Float_t> area;
    TRArray<Float_t> rawFactor;
    TRArray<Int_t> puId;
    TRVariable<Float_t> rho;


    void setSyst();
    void setupJEC(GenericParticle& genJet);

    std::pair<Float_t, Float_t> get_JEC_pair(Systematic syst, size_t idx) const
    {
        if (m_jet_scales.find(syst) == m_jet_scales.end() ||
            m_jet_scales.at(syst).size() == 0) {
            return std::make_pair(1., 1.);
        }
        const auto scales = m_jet_scales.at(syst);
        return std::make_pair(scales.at(eVar::Down).at(idx), scales.at(eVar::Up).at(idx));
    }
    float loose_bjet_cut, medium_bjet_cut, tight_bjet_cut;

    void fillJet(JetOut& output, Level level, size_t pass_bitmap);
    void fillJetEff(BEffOut& output, Level level, size_t pass_bitmap);

private:
    int looseId = 0b11;
    float jet_dr = 0.4;
    std::unordered_map<Systematic, std::unordered_map<eVar, std::vector<float>>> m_jet_scales;
    std::vector<float>* m_jec;

    void createLooseList();
    void createBJetList();
    void createTightList();

    float getHT(const std::vector<size_t>& jet_list);
    float getCentrality(const std::vector<size_t>& jet_list);

    std::unordered_map<Year, std::string> jes_source = {
        {Year::yr2016pre, "Summer19UL16APV_V7_MC"},
        {Year::yr2016post, "Summer19UL16_V7_MC"},
        {Year::yr2017, "Summer19UL17_V5_MC"},
        {Year::yr2018, "Summer19UL18_V5_MC"},
    };

    std::unordered_map<Year, std::string> jer_source = {
        {Year::yr2016pre, "Summer20UL16APV_JRV3_MC"},
        {Year::yr2016post, "Summer20UL16_JRV3_MC"},
        {Year::yr2017, "Summer19UL17_JRV2_MC"},
        {Year::yr2018, "Summer19UL18_JRV2_MC"},
    };

    WeightHolder jer_scale, jet_resolution, jes_scale;
    WeightHolder puid_scale;
    WeightHolder btag_bc_scale, btag_udsg_scale, btag_eff;

    bool use_shape_btag = false;

    std::random_device rd{};
    std::mt19937 gen{rd()};

    float get_jer(size_t i, GenericParticle& genJet);
    float get_jes(size_t i);
};

#endif // __JET_H_
