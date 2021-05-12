#include "analysis_suite/Analyzer/interface/GenParticle.h"

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

void GenParticle::setup(TTreeReader& fReader, Year year, bool isMC_)
{
    isMC = isMC_;
    if (!isMC)
        return;
    Particle::setup("Jet", fReader, year);
    pdgId = new TTRArray<Int_t>(fReader, "GenPart_pdgId");

    setup_map(Level::Top);
}

void GenParticle::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (abs(pdgId->At(i)) == static_cast<Int_t>(PID::Top)) {
            m_partList[Level::Top]->push_back(i);
        }
    }
}
