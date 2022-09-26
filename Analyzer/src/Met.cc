#include "analysis_suite/Analyzer/interface/Met.h"
#include "analysis_suite/Analyzer/interface/Jet.h"

#include "analysis_suite/Analyzer/interface/XYMETCorrection.h"

void Met::setup(TTreeReader& fReader, MET_Type type)
{
    name = met_name[type];
    m_pt.setup(fReader, (name+"_pt").c_str());
    m_phi.setup(fReader, (name+"_phi").c_str());

    m_corr_pt[Systematic::Nominal] = {{eVar::Nominal, 0}};
    m_corr_phi[Systematic::Nominal] = {{eVar::Nominal, 0}};
    for (auto syst : jec_systs) {
        m_corr_pt[syst] = {{eVar::Up, 0}, {eVar::Down, 0}};
        m_corr_phi[syst] = {{eVar::Up, 0}, {eVar::Down, 0}};
    }
}

void Met::setSyst()
{
    if (currentSyst == Systematic::Nominal || isJECSyst()) {
        corr_pt = &m_corr_pt[currentSyst][currentVar];
        corr_phi = &m_corr_phi[currentSyst][currentVar];
    } else {
        corr_pt = &m_corr_pt[Systematic::Nominal][eVar::Nominal];
        corr_phi = &m_corr_phi[Systematic::Nominal][eVar::Nominal];
    }
}

void Met::setupMet(Jet& jet, UInt_t run, int nVertices)
{
    if (currentSyst == Systematic::Nominal || isJECSyst()) {
        (*corr_pt) = *m_pt;
        (*corr_phi) = *m_phi;
        // Get change in Met from change in Jet momentum
        auto met_vec = std::polar(*m_pt, *m_phi) - jet.get_momentum_change();
        (*corr_pt) = std::abs(met_vec);
        (*corr_phi) = std::arg(met_vec);
        pt_unfix = pt();
        phi_unfix = phi();
        fix_xy(run, nVertices);
    }
}

void Met::fix_xy(UInt_t run, int nVertices)
{
    auto met_corr = METXYCorr_Met_MetPhi(pt(), phi(), run, yearMap.at(year_), isMC, nVertices);
    (*corr_pt) = met_corr.first;
    (*corr_phi) = met_corr.second;

}

float Met::mt(float l_pt, float l_phi)
{
    return sqrt(2*pt()*l_pt*(1 - cos(phi() - l_phi)));
}
