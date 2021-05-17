#!/usr/bin/env python3

import os
import sys
import datetime
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
import mplhep as hep
plt.style.use([hep.style.CMS, hep.style.firamath])

import analysis_suite.commons.configs as config
from analysis_suite.commons import writeHTML, PlotInfo, GroupInfo
from analysis_suite.commons.histogram import Histogram
import analysis_suite.data.inputs as plot_params
from .stack import Stack
from .pyPad import pyPad
from .LogFile import LogFile
from .configHelper import setupPathAndDir

def setup(cli_args):
    callTime = str(datetime.datetime.now())
    command = ' '.join(sys.argv)
    LogFile.add_metainfo(callTime, command)
    
    signalNames = cli_args.signal.split(',')
    if not set(signalNames) & set(plot_params.color_by_group.keys()):
        print("signal not in list of groups!")
        print(plot_params.color_by_group.keys())
        exit(1)

    plot_info = PlotInfo(cli_args.info)
    group_info = GroupInfo(plot_params.color_by_group, **vars(cli_args))

    basePath = setupPathAndDir(cli_args.analysis, cli_args.drawStyle,
                               cli_args.workdir, cli_args.years)

    argList = list()
    for year in ["all"] + cli_args.years:
        for histName in plot_info.get_hists():

            argList.append((histName, group_info, plot_info,basePath,
                            cli_args.workdir, signalNames, year))

    return argList


def run(histName, file_info, plot_info, basePath, indir, signalNames, year):
    print(f'Processing {histName} for year {year}')

    baseYear = basePath if year == "all" else f'{basePath}/{year}'
    logger = LogFile(histName, plot_info.at(histName), plot_info.get_lumi(year),
                     f'{baseYear}/logs')
    binning = plot_info.get_binning(histName)
    # Setup histograms
    ratio = Histogram("Ratio", "black", binning)
    band = Histogram("Ratio", "plum", binning)
    error = Histogram("Stat Errors", "plum", binning)
    data = Histogram("Data", "black", binning)
    stacker = Stack(binning)
    groupHists = config.getYearNormedHistos(f'{indir}/{{}}/test.root',
                                            file_info, plot_info, histName, year)
    exclude = ['data'] + signalNames
    signal = groupHists[signalNames[0]] if signalNames[0] in groupHists else None
    # signals = {sig: groupHists[sig] for sig in (sig for sig in signalNames
    #                                          if sig in groupHists)}
    data += groupHists['data'] if 'data' in groupHists else None
    for group in (g for g in groupHists.keys() if g not in exclude):
        stacker += groupHists[group]
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

    pad.setLegend(plot_info.at(histName))
    pad.axisSetup(plot_info.at(histName), stacker.get_xrange())
    hep.cms.label(ax=pad(), data=data, lumi=plot_info.get_lumi(year)) #year=year
    fig = plt.gcf()


    plotBase = f'{baseYear}/plots/{histName}'
    plt.savefig(f'{plotBase}.png', format="png", bbox_inches='tight')
    subprocess.call('convert {0}.png -quality 0 {0}.pdf'.format(plotBase),
                    shell=True)
    plt.close()

    # setup log file
    for group, hist in groupHists.items():
        logger.add_breakdown(group, hist.breakdown)
    logger.add_mc(stacker)
    if signal:
        logger.add_signal(signal)
    logger.write_out()



def cleanup(cli_args):
    basePath = setupPathAndDir(cli_args.analysis, cli_args.drawStyle,
                               cli_args.workdir, cli_args.years)
    writeHTML(basePath, cli_args.analysis, plot_params.all_years)
    for year in cli_args.years:
        writeHTML(f'{basePath}/{year}'
                  f'{cli_args.analysis}/{year}')

    userName = os.environ['USER']
    htmlPath = basePath.split(userName)[1]
    if 'hep.wisc.edu' in os.environ['HOSTNAME']:
        print(f'https://www.hep.wisc.edu/~{userName}/{htmlPath[13:]}')
    else:
        print(f'https://{0}.web.cern.ch/{userName}/{htmlPath[4:]}')
