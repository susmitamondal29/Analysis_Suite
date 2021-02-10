#!/usr/bin/env python3

import os
import sys
import datetime
import subprocess
import multiprocessing as mp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
import mplhep as hep
plt.style.use([hep.style.CMS, hep.style.firamath])

import analysis_suite.commons.configs as config
from analysis_suite.commons import writeHTML, PlotInfo, FileInfo
from analysis_suite.commons.histogram import Histogram
from analysis_suite.data.inputs import plot_params
from .stack import Stack
from .pyPad import pyPad
from .LogFile import LogFile
from .configHelper import setupPathAndDir

def setup(cli_args):
    signalNames = cli_args.signal.split(',')
    if not set(signalNames) & set(plot_params.color_by_group.keys()):
        print("signal not in list of groups!")
        print(plot_params.color_by_group.keys())
        exit(1)

    file_info = FileInfo(plot_params.color_by_group, **vars(cli_args))
    plot_info = PlotInfo(cli_args.info, lumi=cli_args.lumi*1000)
    channels = cli_args.channels.split(',')
    basePath = setupPathAndDir(cli_args.analysis, cli_args.drawStyle, cli_args.workdir,
                               channels)

    argList = list()    
    for histName in plot_info.get_hists():
        argList.append((histName, file_info, plot_info, basePath, cli_args.infile,
                        signalNames, channels))
    return argList


def run(histName, file_info, plot_info, basePath, infileName, signalNames, channels):
    print("Processing {}".format(histName))
    binning = plot_info.get_binning(histName)

    for chan in channels:
        ratio = Histogram("Ratio", "black", binning)
        band = Histogram("Ratio", "plum", binning)
        error = Histogram("Stat Errors", "plum", binning)
        stacker = Stack(binning)

        groupHists = config.getNormedHistos(infileName, file_info, plot_info,
                                            histName, chan)
        exclude = ['data'] + signalNames
        signal = groupHists[signalNames[0]] if signalNames[0] in groupHists else None
        # signals = {sig: groupHists[sig] for sig in (sig for sig in signalNames
        #                                          if sig in groupHists)}
        data = groupHists['data'] if 'data' in groupHists else None
        for group in (g for g in groupHists.keys() if g not in exclude):
            stacker += groupHists[group]
        error += stacker
        # for sig, signal in signals.items():
        if signal:
            # scale = config.findScale(stacker.integral() / signal.integral())
            scale = stacker.integral() / signal.integral()
            signal.scale(scale, forPlot=True)

        # ratio
        if signal:
            ratio += signal / stacker
            ratio.scale(signal.draw_sc, forPlot=True)
            band += stacker/stacker

        # # Extra options
        # stacker.setDrawType(args.drawStyle)

        pad = pyPad(plt, ratio)
        n, bins, patches = pad().hist(**stacker.getInputs())
        stacker.applyPatches(plt, patches)

        # for signal in (s for s in signals.values() if s):
        if signal:
            pad().hist(**signal.getInputsHist())
            pad().errorbar(**signal.getInputs())
        if data:
            pad().errorbar(**data.getInputs())
        if error:
            pad().hist(**error.getInputsError())
        if ratio:
            pad(sub_pad=True).errorbar(**ratio.getInputs())
            pad(sub_pad=True).hist(**band.getInputsError())

        pad.setLegend(plot_info[histName])
        pad.axisSetup(plot_info[histName])
        hep.cms.label(ax=pad(), year="Run II", data=data) # , lumi=info.getLumi()/1000

        fig = plt.gcf()

        if chan == "all" or len(channels) == 1:
            chan = ""
        baseChan = "{}/{}".format(basePath, chan)
        plotBase = "{}/plots/{}".format(baseChan, histName)
        plt.savefig("{}.png".format(plotBase), format="png", bbox_inches='tight')
        subprocess.call('convert {0}.png -quality 0 {0}.pdf'.format(plotBase),
                        shell=True)
        plt.close()

        # # setup log file
        # logger = LogFile(histName, plot_info, "{}/logs".format(baseChan))
        # logger.add_metainfo(callTime, command)
        # logger.add_mc(stacker)
        # if signal:
        #     logger.add_signal(signal)
        # logger.write_out()



def cleanup(cli_args):
    channels = cli_args.channels.split(',')
    try:
        channels.remove("all")
    except ValueError:
        if len(channels) == 1:
            channels = []
        else:
            print("No all channel")

    basePath = setupPathAndDir(cli_args.analysis, cli_args.drawStyle, cli_args.workdir,
                               channels)
    writeHTML(basePath, cli_args.analysis, channels)
    for chan in channels:
        writeHTML("{}/{}".format(basePath, chan), "{}/{}".format(cli_args.analysis, chan))

    userName = os.environ['USER']
    htmlPath = basePath.split(userName)[1]
    if 'hep.wisc.edu' in os.environ['HOSTNAME']:
        print("https://www.hep.wisc.edu/~{0}/{1}".format(userName, htmlPath[13:]))
    else:
        print("https://{0}.web.cern.ch/{0}/{1}".format(userName, htmlPath[4:]))
