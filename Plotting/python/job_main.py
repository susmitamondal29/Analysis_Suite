#!/usr/bin/env python3

import sys
import datetime
from pathlib import Path
import socket
import subprocess
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
import numpy as np

from analysis_suite.commons.plot_utils import plot, setup_mplhep, setup_ticks, axisSetup
import analysis_suite.commons.configs as config
from analysis_suite.commons import writeHTML, PlotInfo, GroupInfo
from analysis_suite.commons.histogram import Histogram
import analysis_suite.data.inputs as plot_params
from .stack import Stack
from .LogFile import LogFile

hep = setup_mplhep()

def setup(cli_args):
    callTime = str(datetime.datetime.now())
    command = ' '.join(sys.argv)
    LogFile.add_metainfo(callTime, command)

    if cli_args.signal not in plot_params.color_by_group:
        logging.error("signal not in list of groups!")
        logging.error(plot_params.color_by_group.keys())
        exit(1)

    plot_info = PlotInfo(cli_args.info)
    group_info = GroupInfo(plot_params.color_by_group, **vars(cli_args))
    basePath = config.get_plot_area(cli_args.analysis, cli_args.drawStyle,
                                    cli_args.workdir)
    config.make_plot_paths(basePath)

    argList = list()
    allSysts = config.get_list_systs(**vars(cli_args))
    for year in cli_args.years:
        path = cli_args.workdir / year
        baseYear = basePath / year
        config.make_plot_paths(baseYear)
        for syst in allSysts:
            filename = path / f'test_{syst}.root'
            outpath = baseYear
            if syst != "Nominal":
                outpath = outpath / syst
                config.make_plot_paths(outpath)
            for histName in plot_info.get_hists(cli_args.hists):
                argList.append((histName, group_info, plot_info, outpath,
                                filename, cli_args.signal, year, syst))

    # for histName in plot_info.get_hists(cli_args.hists):
    #     argList.append((histName, group_info, plot_info, basePath,
    #                     cli_args.workdir / "test_Nominal.root",
    #                     cli_args.signal, "all", "Nominal"))

    return argList


def run(histName, file_info, plot_info, outpath, filename, signalName, year, syst):
    logging.info(f'Processing {histName} for year {year} and systematic {syst}')

    logger = LogFile(histName, plot_info.at(histName), plot_info.get_lumi(year))
    binning = plot_info.get_binning(histName)

    # Setup histograms
    ratio = Histogram("Ratio", binning, color="black")
    band = Histogram("Ratio", binning, color="plum")
    error = Histogram("Stat Errors", binning, color="plum")
    data = Histogram("Data", binning, color="black")

    stacker = Stack(binning)
    groupHists = config.getNormedHistos(filename, file_info, plot_info,
                                        histName, year)
    for group, hist in groupHists.items():
        hist.set_plot_details(file_info)

    signal = groupHists.pop(signalName)
    if "data" in groupHists:
        data += groupHists.pop("data")

    for group, hist in groupHists.items():
        stacker += hist
    error += stacker

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
        plot_inputs["gridspec_kw"]["height_ratio"] = [3, 1]

    plotBase = outpath / 'plots' / histName
    with plot(f"{plotBase}.png", **plot_inputs) as pad:
        if isinstance(pad, np.ndarray):
            pad, subpad = pad
        else:
            subpad = None
        setup_ticks(pad, subpad)

        n, bins, patches = pad.hist(**stacker.getInputs())
        stacker.applyPatches(patches)

        if signal:
            pad.hist(**signal.getInputsHist())
            pad.errorbar(**signal.getInputs())
        if data:
            pad.errorbar(**data.getInputs())
        if error:
            pad.hist(**error.getInputsError())
        if ratio:
            subpad.errorbar(**ratio.getInputs())
            subpad.hist(**band.getInputsError())

        pad.legend(loc=plot_info.get_legend_loc(histName))
        axisSetup(pad, subpad, xlabel=plot_info.get_label(histName), binning=stacker.get_xrange())
        hep.cms.label(ax=pad, data=data, lumi=plot_info.get_lumi(year)) #year=year

    subprocess.call('convert {0}.png -quality 0 {0}.pdf'.format(plotBase), shell=True)


    # setup log file
    for group, hist in groupHists.items():
        logger.add_breakdown(group, hist.breakdown)
    logger.add_mc(stacker)
    if signal:
        logger.add_signal(signal)
    logger.write_out(outpath / 'logs')



def cleanup(cli_args):
    basePath = config.get_plot_area(cli_args.analysis, cli_args.drawStyle,
                                    cli_args.workdir)
    analysis = cli_args.analysis
    allSysts = config.get_list_systs(**vars(cli_args))
    allSysts.remove("Nominal")

    # combined page
    writeHTML(basePath, analysis, plot_params.all_years)
    for year in cli_args.years:
        yearPath = basePath / year
        yearAnalysis = f'{analysis}/{year}'
        writeHTML(yearPath, yearAnalysis, allSysts)
        for syst in allSysts:
            writeHTML(yearPath/syst, f'{yearAnalysis}/{syst}')

    userName = Path.home().owner()
    htmlPath = str(basePath).split(userName)[1]
    if 'hep.wisc.edu' in socket.gethostname():
        logging.critical(f'https://www.hep.wisc.edu/~{userName}/{htmlPath[13:]}')
    else:
        logging.critical(f'https://{userName}.web.cern.ch/{userName}/{htmlPath[4:]}')
