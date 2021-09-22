#!/usr/bin/env python
import uproot4 as up
import sys
import datetime
from pathlib import Path
import socket
import subprocess
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
import mplhep as hep
plt.style.use([hep.style.CMS, hep.style.firamath])

import analysis_suite.commons.configs as config
from analysis_suite.commons import writeHTML, PlotInfo, GroupInfo
from analysis_suite.commons.histogram import Histogram
import analysis_suite.data.inputs as plot_params
from analysis_suite.Plotting.stack import Stack
from analysis_suite.Plotting.LogFile import LogFile

file = up.open("fitDiagnosticsTest.root")


histName = "NJets"
plot_info = PlotInfo('plotInfo_default')
group_info = GroupInfo(plot_params.color_by_group, analysis="ThreeTop")
binning = plot_info.get_binning(histName)
signalName = "ttt"

# Setup histograms
ratio = Histogram("Ratio", binning)
band = Histogram("Ratio", binning)
error = Histogram("Stat Errors", binning)
data = Histogram("Data", binning)
signal = Histogram("Signal", binning)
stacker = Stack(binning)

for key, hist in file["shapes_fit_s/yr2018"].items():
    key = key[:key.index(";")]
    # Need to deal with Data
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

# # for sig, signal in signals.items():
# if signal:
#     # scale = config.findScale(stacker.integral() / signal.integral())
#     scale = stacker.integral() / signal.integral()
#     signal.scale(scale, forPlot=True)

# # # ratio
# if data:
#     ratio += data / stacker
#     # ratio.scale(signal.draw_sc, forPlot=True)
#     band += stacker/stacker

# # Extra options
# stacker.setDrawType(args.drawStyle)

# pad = pyPad(plt, ratio)
# n, bins, patches = pad().hist(**stacker.getInputs())
# stacker.applyPatches(plt, patches)

# # for signal in (s for s in signals.values() if s):
# if signal:
#     pad().hist(**signal.getInputsHist())
#     pad().errorbar(**signal.getInputs())
# if data:
#     pad().errorbar(**data.getInputs())
# if error:
#     pad().hist(**error.getInputsError())
# if ratio:
#     pad(sub_pad=True).errorbar(**ratio.getInputs())
#     pad(sub_pad=True).hist(**band.getInputsError())

# pad.setLegend(plot_info.at(histName))
# pad.axisSetup(plot_info.at(histName), stacker.get_xrange())
# hep.cms.label(ax=pad(), data=data, lumi=plot_info.get_lumi(year)) #year=year
# fig = plt.gcf()


# plotBase = outpath / f'plots/{histName}'
# plt.savefig(f'{plotBase}.png', format="png", bbox_inches='tight')
# subprocess.call('convert {0}.png -quality 0 {0}.pdf'.format(plotBase),
#                 shell=True)
# plt.close()
