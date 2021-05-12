#include "analysis_suite/Analyzer/interface/Jet.h"

void Jet::setup(TTreeReader& fReader, Year year)
{
    Particle::setup("Jet", fReader, year);
    jetId = new TTRArray<Int_t>(fReader, "Jet_jetId");
    hadronFlavour = new TTRArray<Int_t>(fReader, "Jet_hadronFlavour");
    btag = new TTRArray<Float_t>(fReader, "Jet_btagDeepB");

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
}

void Jet::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (pt(i) > 5
            && fabs(eta(i)) < 2.4
            && (jetId->At(i) & looseId) != 0
            && (closeJetDr_by_index.find(i) == closeJetDr_by_index.end() || closeJetDr_by_index.at(i) >= pow(0.4, 2)))
            list(Level::Loose)->push_back(i);
    }
}

void Jet::createBJetList()
{
    for (auto i : *list(Level::Loose)) {
        if (btag->At(i) > medium_bjet_cut)
            list(Level::Bottom)->push_back(i);
        n_loose_bjet.back() += (btag->At(i) > loose_bjet_cut) ? 1 : 0;
        n_medium_bjet.back() += (btag->At(i) > medium_bjet_cut) ? 1 : 0;
        n_tight_bjet.back() += (btag->At(i) > tight_bjet_cut) ? 1 : 0;
    }
}

void Jet::createTightList()
{
    for (auto i : *list(Level::Loose)) {
        if (pt(i) > 40)
            list(Level::Tight)->push_back(i);
    }
}

float Jet::getHT(std::vector<size_t> jet_list)
{
    float ht = 0;
    for (auto i : jet_list) {
        ht += pt(i);
    }
    return ht;
}

float Jet::getCentrality(std::vector<size_t> jet_list)
{
    float etot = 0;
    for (auto i : jet_list) {
        LorentzVector jet(pt(i), eta(i), phi(i), mass(i));
        etot += jet.E();
    }
    return getHT(jet_list) / etot;
}
