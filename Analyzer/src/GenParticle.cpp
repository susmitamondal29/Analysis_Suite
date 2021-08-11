#include "analysis_suite/Analyzer/interface/GenParticle.h"

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

void GenParticle::setup(TTreeReader& fReader)
{
    Particle::setup("GenPart", fReader);
    pdgId = new TTRArray<Int_t>(fReader, "GenPart_pdgId");

    setup_map(Level::Top);
}

void GenParticle::createTopList()
{
    for (size_t i = 0; i < size(); i++) {
        if (abs(pdgId->At(i)) == static_cast<Int_t>(PID::Top)) {
            m_partList[Level::Top]->push_back(i);
        }
    }
}

void GenJet::setup(TTreeReader& fReader)
{
    Particle::setup("GenJet", fReader);

    setup_map(Level::Jet);
}

void GenJet::createJetList(Particle& jet)
{
    // for (size_t i = 0; i < jet.size(); i++) {

    // }
}
