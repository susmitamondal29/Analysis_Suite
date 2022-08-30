#include "analysis_suite/Analyzer/interface/Met.h"
#include "analysis_suite/Analyzer/interface/Jet.h"

void Met::setup(MET_Type type, TTreeReader& fReader)
{
    name = met_name[type];
    m_pt.setup(fReader, (name+"_pt").c_str());
    m_phi.setup(fReader, (name+"_phi").c_str());

    auto corr_set = getScaleFile("USER", "met_xy");

    xcorr = WeightHolder(corr_set->at("x_correction"));
    ycorr = WeightHolder(corr_set->at("y_correction"));

    m_corr_pt[Systematic::Nominal] = {{eVar::Nominal, 0}};
    m_corr_phi[Systematic::Nominal] = {{eVar::Nominal, 0}};
    for (auto syst : jec_systs) {
        m_corr_pt[syst] = {{eVar::Up, 0}, {eVar::Down, 0}};
        m_corr_phi[syst] = {{eVar::Up, 0}, {eVar::Down, 0}};
    }
}

void Met::setupMet(Jet& jet, UInt_t run, int nVertices)
{
    if (currentSyst == Systematic::Nominal || jet.isJECSyst()) {
        // Setup values
        corr_pt = &m_corr_pt[currentSyst][currentVar];
        corr_phi = &m_corr_phi[currentSyst][currentVar];

        // Get change in Met from change in Jet momentum
        auto met_vec = std::polar(*m_pt, *m_phi) - jet.get_momentum_change();
        (*corr_pt) = std::abs(met_vec);
        (*corr_phi) = std::arg(met_vec);
        fix_xy(run, nVertices);
    } else {
        corr_pt = &m_corr_pt[Systematic::Nominal][eVar::Nominal];
        corr_phi = &m_corr_phi[Systematic::Nominal][eVar::Nominal];
    }
}

void Met::fix_xy(UInt_t run, int nVertices)
{
    float corr_metx = pt()*cos(phi())+xcorr.evaluate({name, (float)run, (float)nVertices});
    float corr_mety = pt()*sin(phi())+ycorr.evaluate({name, (float)run, (float)nVertices});

    (*corr_pt) = sqrt(pow(corr_metx, 2) + pow(corr_mety, 2));
    (*corr_phi) = atan2(corr_mety, corr_metx);
}

float Met::mt(float l_pt, float l_phi)
{
    return sqrt(2*pt()*l_pt*(1 - cos(phi() - l_phi)));
}
