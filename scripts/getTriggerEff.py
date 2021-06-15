#!/usr/bin/env python3

import uproot4 as uproot
import numpy as np
from scipy.stats import beta
import boost_histogram as bh

from analysis_suite.commons.histogram import Histogram
from analysis_suite.data.inputs import plot_params

#filename ="result_2018.root"
filename ="output.root"
year = "all"
chans = ["CHAN_MM", "CHAN_EM", "CHAN_ME", "CHAN_EE",]
lumi = plot_params.lumi[year]*1000

class TriggerEff:
    def __init__(self):
        self.hists = dict()
        self.sumw2 = dict()
        self.bins = None

    def add(self, val, err, scale):
        for i, chan in enumerate(chans):
            chanVal = scale*val[i+1][1:-1]
            chanVal[-1] += scale*val[i+1][-1]
            err2Val = (scale*val[i+1][1:-1])**2
            err2Val[-1] += (scale*err[i+1][-1])**2
            if chan not in self.hists:
                self.hists[chan] = chanVal
                self.sumw2[chan] = err2Val
            else:
                self.hists[chan] += chanVal
                self.sumw2[chan] += err2Val
                
    def getSplit(self, chan):
        cumval = np.cumsum(self.hists[chan][::-1])[::-1]
        cumsumw2 = np.cumsum(self.sumw2[chan][::-1])[::-1]
        return cumval, np.sqrt(cumsumw2)


passTrigger = TriggerEff()
allTrigger = TriggerEff()
bins = None
with uproot.open(filename) as f:
    groups = [key.strip(";1") for key in f.keys() if "/" not in key]
    for group in groups:
        xsec = float(f[group]["Xsec"].member("fTitle"))
        sumw = sum(f[group]["sumweight"].values())
        scale = lumi*xsec/sumw
        if bins is None:
            bins = f[group]["passTrigger"].edges(1)[1:-1]
        passVal, passErr = f[group]["passTrigger"].values_errors()
        failVal, failErr = f[group]["failTrigger"].values_errors()

        passTrigger.add(passVal, passErr, scale)
        allTrigger.add(passVal, passErr, scale)
        allTrigger.add(failVal, failErr, scale)


nbins = len(bins) - 1
import ROOT
ROOT.gROOT.SetBatch(True)

for chan in chans:
    passTH1 = ROOT.TH1D("pass_{}".format(chan), "pass_{}".format(chan), nbins, bins)
    pval, psumw = passTrigger.getSplit(chan)
    allTH1 = ROOT.TH1D("all_{}".format(chan), "all_{}".format(chan), nbins, bins)
    aval, asumw = allTrigger.getSplit(chan)

    for b in range(nbins):
        passTH1.SetBinContent(b+1, pval[b])
        passTH1.SetBinError(b+1, psumw[b])
        allTH1.SetBinContent(b+1, aval[b])
        allTH1.SetBinError(b+1, asumw[b])
    eff = ROOT.TEfficiency(passTH1, allTH1)
    
    can = ROOT.TCanvas("canvas", "Trigger Efficiency")
    eff.Draw("ap")
    can.SaveAs("eff_{}.pdf".format(chan))
