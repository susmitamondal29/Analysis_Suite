#include "analysis_suite/skim/interface/GenParticle.h"

#include "analysis_suite/skim/interface/CommonEnums.h"

void GenParticle::setup(TTreeReader& fReader)
{
    GenericParticle::setup("GenPart", fReader);
    pdgId.setup(fReader, "GenPart_pdgId");

    setup_map(Level::Top);
}

void GenParticle::createTopList()
{
    for (size_t i = 0; i < size(); i++) {
        if (abs(pdgId.at(i)) == static_cast<Int_t>(PID::Top)) {
            m_partList[Level::Top]->push_back(i);
        }
    }
}

void GenJet::setup(TTreeReader& fReader)
{
    GenericParticle::setup("GenJet", fReader);

}
