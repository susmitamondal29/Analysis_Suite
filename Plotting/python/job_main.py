#!/usr/bin/env python3
import sys
import datetime
import subprocess
import logging

import analysis_suite.commons.configs as config
import analysis_suite.commons.constants as constants
from analysis_suite.commons import writeHTML, GroupInfo
from analysis_suite.commons.user import website, www_area
from analysis_suite.data.plotInfo.plotInfo import plots

from .plotter import Plotter
from .LogFile import LogFile

def setup(cli_args):
    callTime = str(datetime.datetime.now())
    command = ' '.join(sys.argv)
    LogFile.add_metainfo(callTime, command)

    basePath = config.get_plot_area(cli_args.name, cli_args.workdir)
    config.make_plot_paths(basePath)

    argList = list()
    allSysts = ["Nominal"]
    for year in cli_args.years:
        for syst in allSysts:
            filename = cli_args.workdir / year / f'{cli_args.type}_{syst}_{cli_args.region}.root'
            outpath = basePath / year
            if syst != "Nominal":
                outpath = outpath / syst
            config.make_plot_paths(outpath)
            for plot in plots:
                argList.append((filename, outpath, plot, cli_args.signal, year, syst))
    return argList


def run(infile, outpath, graph, signalName, year, syst):
    logging.info(f'Processing {graph.name} for year {year} and systematic {syst}')
    ginfo = GroupInfo(config.get_inputs(infile.parents[1]).color_by_group)
    groups = ginfo.setup_groups()
    logger = LogFile(graph.name, constants.lumi[year], graph)

    plotter = Plotter(infile, groups, year=year)
    plotter.set_groups(signalName)
    plotter.fill_hists(graph, ginfo)
    plotter.plot_stack(graph.name, outpath/'plots'/f'{graph.name}.png')

    subprocess.call('convert {0}.png -quality 0 {0}.pdf'.format(outpath/'plots'/graph.name), shell=True)

    # setup log file
    # for group, hist in groupHists.items():
    #     logger.add_breakdown(group, hist.breakdown)
    logger.add_mc(plotter.make_stack(graph.name))
    logger.add_signal(plotter.get_hists(graph.name, signalName))
    logger.write_out(outpath/'logs')


def cleanup(cli_args):
    basePath = config.get_plot_area(cli_args.name, cli_args.workdir)
    # combined page
    writeHTML(basePath, cli_args.name, constants.years)
    for year in cli_args.years:
        systs = []
        # systs = [i[1] for i in get_files(cli_args, year) if i[1] != "Nominal"]
        yearAnalysis = f'{cli_args.name}/{year}'
        writeHTML(basePath / year, yearAnalysis, systs)
        for syst in systs:
            writeHTML(basePath / year / syst, f'{yearAnalysis}/{syst}')
    logging.critical(website+str(basePath.relative_to(www_area)))
