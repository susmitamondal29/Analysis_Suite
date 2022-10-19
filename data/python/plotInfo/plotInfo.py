#!/usr/bin/env python3
import numpy as np
import boost_histogram.axis as axis
import awkward as ak
from copy import deepcopy

from analysis_suite.plotting.plotter import GraphInfo

plots = [
    # GraphInfo('signal', '$Disc_{Signal}$', axis.Regular(25, 0, 1), 'Signal'),
    GraphInfo('njets', '$N_{j}$', axis.Regular(12, 0, 12), 'NJets'),
    GraphInfo('nbjets', '$N_{b}$', axis.Regular(7, 0, 7), 'NBJets'),
    GraphInfo('nloosebjets', '$N_{looseb}$', axis.Regular(8, 0, 8), 'NlooseBJets'),
    GraphInfo('ntightbjets', '$N_{tightb}$', axis.Regular(7, 0, 7), 'NtightBJets'),
    GraphInfo('met', '$p_{T}^{miss}$ (GeV)', axis.Regular(20, 0, 500), 'Met'),
    GraphInfo('ht', '$H_{T}$ (GeV)', axis.Regular(20, 0, 1500), 'HT'),
    GraphInfo('ht_b', '$H_{T}(b)$ (GeV)', axis.Regular(20, 0, 1200), 'HT_b'),
    GraphInfo('centrality', '$H_{T}/E$', axis.Regular(20, 0, 1), 'centrality'),
    GraphInfo('j1Pt', '$p_{T}(j_{1})$ (GeV)', axis.Regular(20, 0, 650), 'j1Pt'),
    GraphInfo('j2Pt', '$p_{T}(j_{2})$ (GeV)', axis.Regular(20, 0, 500), 'j2Pt'),
    GraphInfo('j3Pt', '$p_{T}(j_{3})$ (GeV)', axis.Regular(20, 0, 300), 'j3Pt'),
    GraphInfo('j4Pt', '$p_{T}(j_{4})$ (GeV)', axis.Regular(20, 0, 250), 'j4Pt'),
    GraphInfo('j5Pt', '$p_{T}(j_{5})$ (GeV)', axis.Regular(20, 0, 150), 'j5Pt'),
    GraphInfo('j6Pt', '$p_{T}(j_{6})$ (GeV)', axis.Regular(20, 0, 150), 'j6Pt'),
    GraphInfo('j7Pt', '$p_{T}(j_{7})$ (GeV)', axis.Regular(20, 0, 150), 'j7Pt'),
    GraphInfo('j8Pt', '$p_{T}(j_{8})$ (GeV)', axis.Regular(20, 0, 100), 'j8Pt'),
    GraphInfo('b1Pt', '$p_{T}(b_{1})$ (GeV)', axis.Regular(20, 0, 500), 'b1Pt'),
    GraphInfo('b2Pt', '$p_{T}(b_{2})$ (GeV)', axis.Regular(20, 0, 300), 'b2Pt'),
    GraphInfo('b3Pt', '$p_{T}(b_{3})$ (GeV)', axis.Regular(20, 0, 200), 'b3Pt'),
    GraphInfo('b4Pt', '$p_{T}(b_{4})$ (GeV)', axis.Regular(20, 0, 100), 'b4Pt'),
    GraphInfo('l1Pt', '$p_{T}(l_{1})$ (GeV)', axis.Regular(20, 0, 500), 'l1Pt'),
    GraphInfo('l2Pt', '$p_{T}(l_{2})$ (GeV)', axis.Regular(20, 0, 200), 'l2Pt'),
    GraphInfo('lepMass', '$M_{\ell\ell}$ (GeV)', axis.Regular(20, 0, 750), 'lepMass'),
    GraphInfo('jetMass', '$M_{jj}$ (GeV)', axis.Regular(20, 0, 1500), 'jetMass'),
    GraphInfo('lepDR', '$\Delta R_{\ell\ell}$', axis.Regular(25, 0, 6), 'lepDR'),
    GraphInfo('jetDR', '$\Delta R_{jj}$', axis.Regular(25, 0, 6), 'jetDR'),
    GraphInfo('lepcos', '$\cos(\theta_{\ell\ell})$', axis.Regular(20, -1, 1), 'LepCos'),
    GraphInfo('jet1cos', '$\cos(\theta_{j\ell1})$', axis.Regular(20, -1, 1), 'JetLep1_Cos'),
    GraphInfo('jet2cos', '$\cos(\theta_{j\ell2})$', axis.Regular(20, -1, 1), 'JetLep2_Cos'),
    # GraphInfo('top_mass', '$M(\ell, b, p_{T}^{miss})$', axis.Regular(20, 0, 500), 'top_mass'),
]

plots_bdt = deepcopy(plots)
for plot in plots_bdt:
    plot.cuts = "Signal<0.4"


ntuple = [
    GraphInfo("met", '$MET$', axis.Regular(20, 0, 200), lambda vg : vg.get_hist("Met"))
]

combine = {
    # 'ttz_cr' : ("CR-ttz", GraphInfo('nbjets', '$N_{b}$', axis.Regular(7, 0, 7), 'NBJets')),
    # 'ttw_cr' : ("Signal", GraphInfo('nbjets', '$N_{b}$', axis.Regular(7, 0, 7), 'NBJets', cuts="Signal<0.8")),
    # 'signal' : ("Signal", GraphInfo('signal', '$Disc_{Signal}$', axis.Regular(20, 0, 1), 'Signal')),
    'signal' : ("Signal", GraphInfo('nbjets', '$N_{b}$', axis.Regular(7, 0, 7), 'NBJets', cuts="Signal>0.85")),
}

