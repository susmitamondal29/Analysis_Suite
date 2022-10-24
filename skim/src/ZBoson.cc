#include "analysis_suite/skim/interface/ZBoson.h"

void ZBoson::setup(TTreeReader& fReader, Lepton* lepton_)
{
    lepton = lepton_;

    setup_map(Level::MM);
    setup_map(Level::EE);
    setup_map(Level::ZZ);
}

void ZBoson::findZPairs(Lepton* leps, Level level)
{
    for (auto i1 : leps->list(Level::Tight)) { //tightList
        LorentzVector lep1 = leps->p4(i1);
        for (auto i2 : leps->list(Level::Tight)) {
            if (i1 >= i2 || leps->charge(i1) * leps->charge(i2) > 0)
                continue;
            auto z_boson = leps->p4(i2) + lep1;
            z_pt.push_back(z_boson.Pt());
            z_eta.push_back(z_boson.Eta());
            z_phi.push_back(z_boson.Phi());
            z_mass.push_back(z_boson.M());
            m_partList[level]->push_back(z_pt.size()-1);
        }
    }
}

void ZBoson::createEEPairList()
{
    // findZPairs(electron, Level::EE);
}

void ZBoson::createMMPairList()
{
    // findZPairs(muon, Level::MM);
}

void ZBoson::createZZPairList()
{
}

bool ZBoson::hasNoOverlap(size_t z1, size_t z2, Level level)
{
    auto list = (level == Level::MM) ? mu_pairs : el_pairs;
    auto pair1 = list.at(z1);
    auto pair2 = list.at(z2);
    return pair1.first != pair2.first;//to-do fix
}
