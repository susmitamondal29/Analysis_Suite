#include "analysis_suite/Analyzer/interface/Jet.h"
#include "analysis_suite/Analyzer/interface/JetCorrection.h"

void Jet::setup(TTreeReader& fReader, bool isMC)
{
    GenericParticle::setup("Jet", fReader);
    jetId = new TTRArray<Int_t>(fReader, "Jet_jetId");
    btag = new TTRArray<Float_t>(fReader, "Jet_btagDeepB");
    area = new TTRArray<Float_t>(fReader, "Jet_area");
    puId = new TTRArray<Int_t>(fReader, "Jet_puId");
    if (isMC) {
        hadronFlavour = new TTRArray<Int_t>(fReader, "Jet_hadronFlavour");
        genJetIdx = new TTRArray<Int_t>(fReader, "Jet_genJetIdx");
        rawFactor = new TTRArray<Float_t>(fReader, "Jet_rawFactor");
        rho = new TTreeReaderValue<Float_t>(fReader, "fixedGridRhoFastjetAll");
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
    // calib = BTagCalibration("deepcsv", scaleDir_ + "/btagging/DeepCSV_" + btag_file[year_] + ".csv");
    calib = BTagCalibration("deepcsv", scaleDir_ + "/btagging/DeepCSV_" + yearMap.at(year_) + ".csv");
    setSF<TH2D>("btagEff_b", Systematic::BJet_Eff);
    setSF<TH2D>("btagEff_c", Systematic::BJet_Eff);
    setSF<TH2D>("btagEff_udsg", Systematic::BJet_Eff);

    use_shape_btag = true;
    createBtagReaders();

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
            && (jetId->At(i) & looseId) != 0
            && (pt(i) > 50 || (puId->At(i) >> PU_Medium) & 1)
            && (closeJetDr_by_index.find(i) == closeJetDr_by_index.end() || closeJetDr_by_index.at(i) >= pow(0.4, 2)))
            m_partList[Level::Loose]->push_back(i);
    }
}

void Jet::createBJetList()
{
    for (auto i : list(Level::Loose)) {
        if (pt(i) > 25
            && btag->At(i) > medium_bjet_cut)
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
    if (use_shape_btag) {
        return getTotalShapeWeight();
    } else {
        return getTotalBTagWeight();

    }
}

float Jet::getTotalBTagWeight() {
    float weight = 1;
    const auto& goodBJets = list(Level::Bottom);
    for (auto bidx : goodBJets) {
        auto btagInfo = btagInfo_by_flav[std::abs(hadronFlavour->At(bidx))];
        weight *= getBWeight(btagInfo.flavor_type, bidx);
    }

    for (auto jidx : list(Level::Tight)) {
        if (std::find(goodBJets.begin(), goodBJets.end(), jidx) != goodBJets.end()) {
            continue; // is a bjet, weighting already taken care of
        }
        auto btagInfo = btagInfo_by_flav[std::abs(hadronFlavour->At(jidx))];
        float eff = getWeight(btagInfo.jet_type, pt(jidx), fabs(eta(jidx)));
        float bSF = getBWeight(btagInfo.flavor_type, jidx);
        weight *= (1 - bSF * eff) / (1 - eff);
    }
    return weight;
}

float Jet::getTotalShapeWeight() {
    float weight = 1;
    const auto bjets = list(Level::Bottom);
    const auto jets = list(Level::Tight);
    std::vector<size_t> jet_list;
    jet_list.reserve(size());
    std::merge(bjets.begin(), bjets.end(), jets.begin(), jets.end(), std::back_inserter(jet_list));
    bool charmSyst = charm_systs.find(currentSyst) != charm_systs.end();


    for (auto idx : jet_list) {
        switch (std::abs(hadronFlavour->At(idx))) {
        case static_cast<Int_t>(PID::Bottom):
            if (!charmSyst) weight *= getShapeWeight(BTagEntry::FLAV_B, idx);
        case static_cast<Int_t>(PID::Charm):
            if (charmSyst) weight *= getShapeWeight(BTagEntry::FLAV_C, idx);
        default:
            if (!charmSyst) weight *= getShapeWeight(BTagEntry::FLAV_UDSG, idx);
        }
    }
    return weight;
}

void Jet::createBtagReaders()
{
    if (use_shape_btag) {
        std::vector<std::string> systs;
        for (auto [syst, name]: systName_by_syst) {
            systs.push_back("up_"+name);
            systs.push_back("down_"+name);
        }
        btag_reader = new BTagCalibrationReader(BTagEntry::OP_RESHAPING, "central", systs);
        btag_reader->load(calib, BTagEntry::FLAV_B, "iterativefit");
        btag_reader->load(calib, BTagEntry::FLAV_C, "iterativefit");
        btag_reader->load(calib, BTagEntry::FLAV_UDSG, "iterativefit");
    } else {
        btag_reader = new BTagCalibrationReader(BTagEntry::OP_MEDIUM, "central", {"up", "down"});
        btag_reader->load(calib, BTagEntry::FLAV_B, "comb");
        btag_reader->load(calib, BTagEntry::FLAV_C, "comb");
        btag_reader->load(calib, BTagEntry::FLAV_UDSG, "incl");
    }
}

void Jet::setupJEC(JetCorrection& jecCorr, GenericParticle& genJet) {
    if (isJECSyst()) {
        m_jec = &m_jet_scales[currentSyst][currentVar];
        for(size_t i = 0; i < size(); ++i) {
            float jes_scale = jecCorr.getJES(nompt(i), eta(i));
            float genPt = (genJetIdx->At(i) != -1) ? genJet.pt(genJetIdx->At(i)) : -1.0;
            float jer_scale = jecCorr.getJER(jes_scale*nompt(i), eta(i), **rho, genPt);
            m_jec->push_back(jes_scale*jer_scale);
        }
    } else {
        m_jec = &m_jet_scales[Systematic::Nominal][eVar::Nominal];
        if (currentSyst == Systematic::Nominal) {
            m_jec->assign(size(), 1);
        }
    }
}
