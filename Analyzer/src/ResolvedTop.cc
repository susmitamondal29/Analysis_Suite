#include "analysis_suite/Analyzer/interface/ResolvedTop.h"
#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

void ResolvedTop::setup(TTreeReader& fReader)
{
    GenericParticle::setup("FatJet", fReader);
    mass_softdrop.setup(fReader, "msoftdrop");
    tau2.setup(fReader, "tau2");
    tau3.setup(fReader, "tau3");

    setup_map(Level::Loose);

    wp = wp_by_name.at("VL");
}

void ResolvedTop::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (mass_softdrop.at(i) > 105
            && mass_softdrop.at(i) < 210
            && tau3.at(i)/tau2.at(i) < wp)
            m_partList[Level::Loose]->push_back(i);
    }
}

float ResolvedTop::getScaleFactor(const Particle& genPart)
{
    float weight = 1.;
    return weight;
}
