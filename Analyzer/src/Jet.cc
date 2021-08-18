#include "analysis_suite/Analyzer/interface/Jet.h"

void Jet::setup(TTreeReader& fReader, bool isMC)
{
    GenericParticle::setup("Jet", fReader);
    jetId = new TTRArray<Int_t>(fReader, "Jet_jetId");
    btag = new TTRArray<Float_t>(fReader, "Jet_btagDeepB");
    area = new TTRArray<Float_t>(fReader, "Jet_area");
    if (isMC) {
        hadronFlavour = new TTRArray<Int_t>(fReader, "Jet_hadronFlavour");
        genJetIdx = new TTRArray<Int_t>(fReader, "Jet_genJetIdx");
        rawFactor = new TTRArray<Float_t>(fReader, "Jet_rawFactor");
    }

    setup_map(Level::Loose);
    setup_map(Level::Bottom);
    setup_map(Level::Tight);

    if (year_ == Year::yr2016) {
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

    calib = BTagCalibration("deepcsv", scaleDir_ + "/scale_factors/btag_" + yearStr_ + ".csv");
    setSF<TH2D>("btagEff_b", Systematic::BJet_Eff);
    setSF<TH2D>("btagEff_c", Systematic::BJet_Eff);
    setSF<TH2D>("btagEff_udsg", Systematic::BJet_Eff);

    createBtagReader(eVar::Nominal);
    createBtagReader(eVar::Down);
    createBtagReader(eVar::Up);
}

void Jet::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 5
            && fabs(eta(i)) < 2.4
            && (jetId->At(i) & looseId) != 0
            && (closeJetDr_by_index.find(i) == closeJetDr_by_index.end() || closeJetDr_by_index.at(i) >= pow(0.4, 2)))
            m_partList[Level::Loose]->push_back(i);
    }
}

void Jet::createBJetList()
{
    for (auto i : list(Level::Loose)) {
        if (btag->At(i) > medium_bjet_cut)
            m_partList[Level::Bottom]->push_back(i);
        n_loose_bjet.back() += (btag->At(i) > loose_bjet_cut) ? 1 : 0;
        n_medium_bjet.back() += (btag->At(i) > medium_bjet_cut) ? 1 : 0;
        n_tight_bjet.back() += (btag->At(i) > tight_bjet_cut) ? 1 : 0;
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

float Jet::getCentrality(const std::vector<size_t>& jet_list)
{
    float etot = 0;
    for (auto i : jet_list) {
        LorentzVector jet(pt(i), eta(i), phi(i), mass(i));
        etot += jet.E();
    }
    return getHT(jet_list) / etot;
}

float Jet::getScaleFactor()
{
    float weight = 1.;
    const auto& goodBJets = list(Level::Bottom);

    for (auto bidx : goodBJets) {
        switch (std::abs(hadronFlavour->At(bidx))) {
        case static_cast<Int_t>(PID::Bottom):
            weight *= getBWeight(BTagEntry::FLAV_B, bidx);
        case static_cast<Int_t>(PID::Charm):
            weight *= getBWeight(BTagEntry::FLAV_C, bidx);
        default:
            weight *= getBWeight(BTagEntry::FLAV_UDSG, bidx);
        }
    }

    for (auto jidx : list(Level::Tight)) {
        if (std::find(goodBJets.begin(), goodBJets.end(), jidx) != goodBJets.end()) {
            continue; // is a bjet, weighting already taken care of
        }
        float eff, bSF;
        switch (std::abs(hadronFlavour->At(jidx))) {
        case static_cast<Int_t>(PID::Bottom):
            bSF = getBWeight(BTagEntry::FLAV_B, jidx);
            eff = getWeight("btagEff_b", pt(jidx), fabs(eta(jidx)));
        case static_cast<Int_t>(PID::Charm):
            bSF = getBWeight(BTagEntry::FLAV_C, jidx);
            eff = getWeight("btagEff_c", pt(jidx), fabs(eta(jidx)));
        default:
            bSF = getBWeight(BTagEntry::FLAV_UDSG, jidx);
            eff = getWeight("btagEff_udsg", pt(jidx), fabs(eta(jidx)));
        }
        weight *= (1 - bSF * eff) / (1 - eff);
    }

    return weight;
}
