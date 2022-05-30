#include "analysis_suite/Analyzer/interface/Jet.h"

void Jet::setup(TTreeReader& fReader, bool isMC)
{
    GenericParticle::setup("Jet", fReader);
    jetId.setup(fReader, "Jet_jetId");
    btag.setup(fReader, "Jet_btagDeepB");
    area.setup(fReader, "Jet_area");
    puId.setup(fReader, "Jet_puId");
    if (isMC) {
        hadronFlavour.setup(fReader, "Jet_hadronFlavour");
        genJetIdx.setup(fReader, "Jet_genJetIdx");
        rawFactor.setup(fReader, "Jet_rawFactor");
        rho.setup(fReader, "fixedGridRhoFastjetAll");
    }

    setup_map(Level::Loose);
    setup_map(Level::Bottom);
    setup_map(Level::Tight);

    if (year_ == Year::yr2016pre || year_ == Year::yr2016post) {
        loose_bjet_cut = 0.2219;
        medium_bjet_cut = 0.6324;
        tight_bjet_cut = 0.8958;

    } else if (year_ == Year::yr2017) {
        loose_bjet_cut = 0.1522;
        medium_bjet_cut = 0.4941;
        tight_bjet_cut = 0.8001;
    } else if (year_ == Year::yr2018) {
        loose_bjet_cut = 0.1241;
        medium_bjet_cut = 0.4184;
        tight_bjet_cut = 0.7527;
    }

    // use_shape_btag = true;

    auto corr_set = getScaleFile("JME", "jet_jerc");
    jec_scale = WeightHolder(corr_set->at(jec_source[year_]+"_Total_AK4PFchs"));
    jet_resolution = WeightHolder(corr_set->at(jer_source[year_]+"_PtResolution_AK4PFchs"));
    jer_scale = WeightHolder(corr_set->at(jer_source[year_]+"_ScaleFactor_AK4PFchs"),
                             Systematic::Jet_JER, {"nom","up","down"});


    m_jet_scales[Systematic::Nominal] = {{eVar::Nominal, std::vector<float>()}};
    for (auto syst : jec_systs) {
        m_jet_scales[syst] = {
            {eVar::Up, std::vector<float>()},
            {eVar::Down, std::vector<float>()}
        };
    }
}

void Jet::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 5
            && fabs(eta(i)) < 2.4
            && (jetId.at(i) & looseId) != 0
            && (pt(i) > 50 || (puId.at(i) >> PU_Medium) & 1)
            && (closeJetDr_by_index.find(i) == closeJetDr_by_index.end() || closeJetDr_by_index.at(i) >= pow(0.4, 2)))
            m_partList[Level::Loose]->push_back(i);
    }
}

void Jet::createBJetList()
{
    for (auto i : list(Level::Loose)) {
        if (pt(i) > 25
            && btag.at(i) > medium_bjet_cut)
            m_partList[Level::Bottom]->push_back(i);
        n_loose_bjet.back() += (btag.at(i) > loose_bjet_cut) ? 1 : 0;
        n_medium_bjet.back() += (btag.at(i) > medium_bjet_cut) ? 1 : 0;
        n_tight_bjet.back() += (btag.at(i) > tight_bjet_cut) ? 1 : 0;
    }
}

void Jet::createTightList()
{
    for (auto i : list(Level::Loose)) {
        if (pt(i) > 40)
            m_partList[Level::Tight]->push_back(i);
    }
}

float Jet::getHT(const std::vector<size_t>& jet_list)
{
    float ht = 0;
    for (auto i : jet_list) {
        ht += pt(i);
    }
    return ht;
}

float Jet::getScaleFactor()
{
    return 1.;
}

float Jet::getCentrality(const std::vector<size_t>& jet_list)
{
    float etot = 0;
    for (auto i : jet_list) {
        etot += p4(i).E();
    }
    return getHT(jet_list) / etot;
}

void Jet::setupJEC(GenericParticle& genJet) {
    if (currentSyst == Systematic::Nominal || isJECSyst()) {
        m_jec = &m_jet_scales[currentSyst][currentVar];
        m_jec->assign(size(), 1);
        for(size_t i = 0; i < size(); ++i) {
            (*m_jec)[i] *= get_jec(i);
            (*m_jec)[i] *= get_jer(i, genJet);
        }
    } else {
        m_jec = &m_jet_scales[Systematic::Nominal][eVar::Nominal];
    }
}

float Jet::get_jec(size_t i) {
    if (currentSyst != Systematic::Jet_JER || currentVar == eVar::Nominal) {
        return 1.;
    } else {
        float delta = jec_scale.evaluate({eta(i), pt(i)});
        return (currentVar == eVar::Up) ? (1+delta) : (1-delta);
    }
}

float Jet::get_jer(size_t i, GenericParticle& genJets) {
    using namespace ROOT::Math::VectorUtil;
    float resolution = jet_resolution.evaluate({eta(i), pt(i), *rho});
    float scale = jer_scale.evaluate({eta(i), systName(jer_scale)});

    bool hasGenJet = genJetIdx.at(i) != -1;
    auto genJet = (hasGenJet) ? genJets.p4(genJetIdx.at(i)) : LorentzVector();
    float pt_ratio = (hasGenJet) ? 1-pt(i)/genJet.Pt() : 0.;

    if (hasGenJet && DeltaR(p4(i), genJet) < jet_dr/2 && abs(pt_ratio) < 3*resolution) {
        return 1 + (scale-1)*pt_ratio;
    } else if (scale > 1.) {
        std::normal_distribution<> gaussian{0, resolution};
        return 1 + gaussian(gen)*sqrt(pow(scale,2) - 1);
    }

    return 1.;
}
