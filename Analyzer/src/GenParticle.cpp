#include "analysis_suite/Analyzer/interface/GenParticle.h"

#include "analysis_suite/Analyzer/interface/CommonEnums.h"

void GenParticle::setup(TTreeReader& fReader, int year, bool isMC_)
{
    isMC = isMC_;
    if (!isMC)
        return;
    Particle::setup("Jet", fReader, year);
    pdgId = new TTRArray<Int_t>(fReader, "GenPart_pdgId");
}

void GenParticle::createLooseList()
{
    for (size_t i = 0; i < pt->GetSize(); i++) {
        if (abs(pdgId->At(i)) == PID_TOP) {
            topList.push_back(i);
        }
    }
}
