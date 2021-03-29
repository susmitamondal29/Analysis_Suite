#!/usr/bin/env python3
from contextlib import contextmanager
import ROOT
from scaleInfo import info


@contextmanager
def rootOpen(filename):
    rootfile = ROOT.TFile(filename, "RECREATE")
    yield rootfile
    rootfile.Close()


def fillMuonSF(info, year, yearDir):
    f = ROOT.TFile(info["Name"][0].format(year))
    histogram = getattr(f, info["Histogram"][year]).Clone("muonSF")
    yearDir.cd()
    histogram.Write()


def fillElectronSF(info, year, yearDir):
    lowf = ROOT.TFile(info["Name"][0])
    lowHistogram = getattr(lowf, "EGamma_SF2D").Clone("electronSF_low")

    highf = ROOT.TFile(info["Name"][1])
    histogram = getattr(highf, "EGamma_SF2D").Clone("electronSF")

    yearDir.cd()
    lowHistogram.Write()
    histogram.Write()
        

def fillSusyElectronSF(info, year, yearDir):
    f = ROOT.TFile(info["Name"].format(year))
    tightHist, looseHist = None, None
    for tightSF in info["TightList"]:
        if tightHist is None:
            tightHist = getattr(f, tightSF.format(year)).Clone("electronSF_susy")
        else:
            tightHist.Multiply(getattr(f, tightSF.format(year)))

    # for tightSF in info["LooseList"]:
    #     if tightHist is None:
    #         tightHist = getattr(f, tightSF).Clone("ElectronSF_susy")
    #     else:
    #         tightHist.Multiply(getattr(f, tightSF))
    yearDir.cd()
    tightHist.Write()
    # looseHist.Write()

def fillPileupSF(info, year, yearDir):
    f = ROOT.TFile(info["Name"])
    histogram = getattr(f, "pileupSF_{}_nom".format(year)).Clone("pileupSF")
    yearDir.cd()
    histogram.Write()
    

def fillTopSF(info, year, yearDir):
    allWP = ["LWP", "MWP", "AltTWP", "TWP"]
    for wp in allWP:
        f = ROOT.TFile(info["Name"].format(wp))
        sig = getattr(f, "{}/hSF_SIG".format(year)).Clone("topSF_{}_True".format(wp))
        bg = getattr(f, "{}/hSF_BG".format(year)).Clone("topSF_{}_Fake".format(wp))
        yearDir.cd()
        sig.Write()
        bg.Write()

def fillBTagEff(info, year, yearDir):
    f = ROOT.TFile(info["Name"])
    for histName in info["Histogram"]:
        f.cd()
        name = "btag"+histName[histName.find("_Eff")+1:]
        histogram = getattr(f, histName).Clone(name)
        yearDir.cd()
        histogram.Write()

years = [2016, 2017, 2018]

with rootOpen("event_scalefactors.root") as outfile:
    for year in years:
        outfile.mkdir(str(year))
        yearDir = getattr(outfile, str(year))
        fillMuonSF(info["muonSF"], year, yearDir)
        fillElectronSF(info["RECOElectronSF"][year], year, yearDir)
        fillSusyElectronSF(info["SUSYElectronSF"], year, yearDir)
        fillPileupSF(info["pileup"], year, yearDir)
        fillTopSF(info["topTagger"], year, yearDir)
        fillBTagEff(info["btagEfficiency"], year, yearDir)

import uproot4 as uproot

with uproot.open("event_scalefactors.root") as f:
    print(f["2016"].keys())
    # print(f["2017"].keys())
    # print(f["2018"].keys())
