#include "analysis_suite/Analyzer/interface/ResolvedTop.h"
#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

void ResolvedTop::setup(TTreeReader& fReader)
{
    GenericParticle::setup("ResolvedTop", fReader);
    discriminator.setup(fReader, "ResolvedTop_discriminator");

    setup_map(Level::Loose);

    std::string workingPoint = "TWP";
    wp = wp_by_name.at(workingPoint);
}

void ResolvedTop::createLooseList()
{
    for (size_t i = 0; i < size(); i++) {
        if (discriminator.at(i) > wp)
            m_partList[Level::Loose]->push_back(i);
    }
}

float ResolvedTop::getScaleFactor(const Particle& genPart)
{
    float weight = 1.;
    return weight;
}
