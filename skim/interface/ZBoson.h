#ifndef ZBOSON_H_
#define ZBOSON_H_

#include "analysis_suite/skim/interface/Particle.h"
#include "analysis_suite/skim/interface/Lepton.h"

class ZBoson : public Particle {
public:
    void setup(TTreeReader& fReader, Lepton* electron_, Lepton* muon_);

    void setupGoodLists() override
    {
        createEEPairList();
        createMMPairList();
        createZZPairList();
    }

    virtual void clear() override
    {
        Particle::clear();
        z_pt.clear();
        z_eta.clear();
        z_phi.clear();
        z_mass.clear();
    }

private:
    void findZPairs(Lepton* leps, Level level);

    void createEEPairList();
    void createMMPairList();
    void createZZPairList();

    bool hasNoOverlap(size_t z1, size_t z2, Level level);

    Float_t pt_(size_t idx) const override { return z_pt.at(idx); }
    Float_t eta_(size_t idx) const override { return z_eta.at(idx); }
    Float_t phi_(size_t idx) const override { return z_phi.at(idx); }
    Float_t mass_(size_t idx) const override { return z_mass.at(idx); }
    size_t size_() const override { return z_pt.size(); }

    std::vector<float> z_pt, z_eta, z_phi, z_mass;
    const float ZMASS = 91.188;
    const float ZWINDOW = 15;

    Lepton *electron, *muon;

    std::vector<std::pair<size_t, size_t>> mu_pairs, el_pairs;
};


#endif // ZBOSON_H_
