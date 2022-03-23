#!/usr/bin/env python3

import uproot
import numpy as np
from scipy.stats import beta
import boost_histogram as bh
import ROOT
ROOT.gROOT.SetBatch(True)

from analysis_suite.commons.histogram import Histogram
from analysis_suite.commons.info import PlotInfo
import analysis_suite.data.inputs as plot_params

#filename ="result_2018.root"
filename ="output.root"
year = "all"
chans = ["CHAN_MM", "CHAN_EM", "CHAN_ME", "CHAN_EE",]
# lumi = plot_params.lumi[year]*1000
lumi = 1000*PlotInfo.lumi[year]

class TriggerEff:
    def __init__(self, updir, scale):
        self.pass_hist = updir["passTrigger"].to_boost()*scale
        self.all_hist = updir["failTrigger"].to_boost()*scale + self.pass_hist
        self.size = self.pass_hist.axes[1].size
        self.axis = self.pass_hist.axes[1].edges

    def cumsum(self, hist):
        return np.cumsum(hist[::-1])[::-1]

    def bins(self, chan, hist):
        a = np.arange(self.size)+1
        b = self.cumsum(hist.view()[chan].value)
        c = self.cumsum(hist.view()[chan].variance)
        return np.dstack([a, b, c])[0]

    def fill_th1(self, th1_pass, th1_all, chan):
        for i, value, variance in self.bins(chan, self.pass_hist):
            th1_pass.SetBinContent(int(i), value)
            th1_pass.SetBinError(int(i), np.sqrt(variance))
        for i, value, variance in self.bins(chan, self.all_hist):
            th1_all.SetBinContent(int(i), value)
            th1_all.SetBinError(int(i), np.sqrt(variance))

# passTrigger = TriggerEff()
# allTrigger = TriggerEff()
# bins = None

def get_tlist_var(tlist, varName):
    for item in tlist:
        if item.member('fName') == varName:
            return item.member('fTitle')
    return None

with uproot.open(filename) as f:
    groups = [key.strip(";1") for key in f.keys() if "/" not in key]
    for group in groups:
        xsec = float(get_tlist_var(f[group]["MetaData"], "Xsec"))
        sumw = sum(f[group]["sumweight"].values())
        scale = lumi*xsec/sumw
        trig = TriggerEff(f[group], scale)

        nbins = trig.size
        for nchan, chan in enumerate(chans):
            passTH1 = ROOT.TH1D("pass_{}".format(chan), "pass_{}".format(chan), trig.size, trig.axis)
            allTH1 = ROOT.TH1D("all_{}".format(chan), "all_{}".format(chan), trig.size, trig.axis)
            trig.fill_th1(passTH1, allTH1, nchan)
            eff = ROOT.TEfficiency(passTH1, allTH1)
            can = ROOT.TCanvas("canvas", "Trigger Efficiency")
            eff.Draw("ap")
            can.SaveAs("eff_{}.pdf".format(chan))
