#!/usr/bin/env python
import uproot4 as up
import sys
import datetime
from pathlib import Path
import socket
import subprocess
import numpy as np

from analysis_suite.commons.plot_utils import plot, setup_mplhep, setup_ticks, axisSetup
import analysis_suite.commons.configs as config
from analysis_suite.commons import writeHTML, PlotInfo, GroupInfo
from analysis_suite.commons.histogram import Histogram
import analysis_suite.data.inputs as plot_params
from analysis_suite.Plotting.stack import Stack
from analysis_suite.Plotting.LogFile import LogFile

hep = setup_mplhep()

file = up.open("fitDiagnosticsTest.root")

histName = 'NJets'
year = "2018"
plot_info = PlotInfo('plotInfo_default')
group_info = GroupInfo(plot_params.color_by_group, analysis="ThreeTop")
binning = plot_info.get_binning(histName)
signalName = "ttt"


# Setup histograms
ratio = Histogram("Ratio", binning, color="black")
band = Histogram("Ratio", binning, color="plum")
error = Histogram("Stat Errors", binning, color='plum')
data = Histogram("Data", binning, color='black')
signal = Histogram("Signal", binning, color="crimson")
stacker = Stack(binning)

for key, hist in file["shapes_fit_s/yr2018"].items():
    key = key[:key.index(";")]
    # Need to deal with Data
    if "data" in key:
        x, y = hist.member("fX"), hist.member("fY")
        data += data.fill(x, weight=y)
    if "TH1" not in repr(hist):
        continue
    hist = hist.to_boost()
    if "total" in key:
        continue
    elif key == signalName:
        signal += hist


    groupHist = Histogram(key, hist.axes[0])
    groupHist.set_plot_details(group_info)
    groupHist += hist
    stacker += groupHist

error += stacker

# for sig, signal in signals.items():
if signal:
    # scale = config.findScale(stacker.integral() / signal.integral())
    scale = stacker.integral() / signal.integral()
    signal.scale(scale, forPlot=True)

# # ratio

if data:
    ratio += data / stacker
    # ratio.scale(signal.draw_sc, forPlot=True)
    band += stacker/stacker

# # Extra options
# stacker.setDrawType(args.drawStyle)

plot_inputs = {"nrows": 1, "ncols": 1, "sharex": True, "gridspec_kw": {"hspace": 0.1}}
if ratio:
    plot_inputs["nrows"] = 2
    plot_inputs["gridspec_kw"]["height_ratios"] = [3, 1]

plotBase = 'plots/' +  histName
with plot(f"{plotBase}.png", **plot_inputs) as pad:
    pad, subpad = pad if isinstance(pad, np.ndarray) else (pad, None)
    setup_ticks(pad, subpad)

    # Upper pad stuff
    stacker.plot_stack(pad)
    signal.plot_points(pad)
    data.plot_points(pad)
    error.plot_band(pad)

    # Lower pad stuff
    ratio.plot_points(subpad)
    band.plot_band(subpad)

    # Finishing Touches
    pad.legend(loc=plot_info.get_legend_loc(histName))
    axisSetup(pad, subpad, xlabel=plot_info.get_label(histName), binning=stacker.get_xrange())
    hep.cms.label(ax=pad, data=data, lumi=plot_info.get_lumi(year)) #year=year

subprocess.call('convert {0}.png -quality 0 {0}.pdf'.format(plotBase), shell=True)
