#include "analysis_suite/Analyzer/interface/ResolvedTop.h"
#include "analysis_suite/Analyzer/interface/CommonFuncs.h"

void ResolvedTop::setup(TTreeReader& fReader)
{
    GenericParticle::setup("FatJet", fReader);
    mass_softdrop.setup(fReader, "FatJet_msoftdrop");
    tau2.setup(fReader, "FatJet_tau2");
    tau3.setup(fReader, "FatJet_tau3");

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

float ResolvedTop::getScaleFactor()
{
    float weight = 1.;
    return weight;
}

void ResolvedTop::fillTop(TopOut& output, Level level, size_t pass_bitmap)
{
    output.clear();
    for (size_t idx = 0; idx < size(); ++idx) {
        size_t final_bitmap = fillParticle(output, level, idx, pass_bitmap);
        if (final_bitmap != 0) {
            output.disc.push_back(tau3.at(idx)/tau2.at(idx));
        }
    }
}
