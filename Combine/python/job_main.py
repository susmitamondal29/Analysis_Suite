#!/usr/bin/env python3
import logging
from pathlib import Path
import uproot as upwrite

from analysis_suite.commons import GroupInfo, PlotInfo
from analysis_suite.commons.configs import getGroupDict, get_list_systs, getNormedHistos, checkOrCreateDir

from .card_maker import Card_Maker

import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(mva_params.color_by_group, **vars(cli_args))
    plot_info = PlotInfo(cli_args.info)

    workdir = cli_args.workdir / "combine"
    checkOrCreateDir(workdir)

    histName = "NJets"

    argList = list()
    for year in cli_args.years:
        inpath = cli_args.workdir/year
        allSysts = get_list_systs(inpath, cli_args.systs)
        # for syst in allSysts:
        argList.append((inpath, workdir, group_info, plot_info, histName, year))

    return argList

def run(inpath, outpath, file_info, plot_info, histName, year):

    groupHists = getNormedHistos(inpath/"test_Nominal.root", file_info, plot_info,
                                 histName, year)

    with upwrite.recreate(outpath / f'{histName}_{year}.root') as f:
        for group, hist in groupHists.items():
            f[group] = hist.hist.to_numpy()
    print("here")

    


def cleanup(cli_args):
    group_info = GroupInfo(mva_params.color_by_group, **vars(cli_args))
    group_list = list(group_info.get_memberMap().keys())
    group_list.remove(cli_args.signal)
    group_list.insert(0, cli_args.signal)

    with Card_Maker(cli_args.workdir, cli_args.years, group_list) as card:
        card.write_systematics(mva_params.systematics)
