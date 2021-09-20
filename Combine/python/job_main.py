#!/usr/bin/env python3
import logging
from pathlib import Path
import uproot as upwrite
import numpy as np

from analysis_suite.commons import GroupInfo, PlotInfo
from analysis_suite.commons.configs import getGroupDict, get_list_systs, checkOrCreateDir, clean_syst
from .histogram_creater import getNormedHistos

from .card_maker import Card_Maker
from .hist_writer import from_boost

import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(mva_params.color_by_group, **vars(cli_args))
    plot_info = PlotInfo(cli_args.info)
    allSysts = get_list_systs(**vars(cli_args))

    workdir = cli_args.workdir / "combine"
    checkOrCreateDir(workdir)

    argList = list()
    for year in cli_args.years:
        inpath = cli_args.workdir/year

        argList.append((inpath, workdir, group_info, plot_info, cli_args.fit_var, year, allSysts))

    return argList

def run(inpath, outpath, file_info, plot_info, histName, year, systs):
    with upwrite.recreate(outpath / f'{histName}_yr{year}.root') as f:
        for syst in systs:
            groupHists = getNormedHistos(inpath/f"test_{syst}.root", file_info,
                                         plot_info, histName, year)
            syst = syst.replace("_up", "Up").replace("_down", "Down")
            if syst == "Nominal":
                groupHists["data_obs"] = np.array(list(groupHists.values())).sum()
            for group, hist in groupHists.items():
                f[f"{group}_{syst}"] = from_boost(hist.hist, histName)


def cleanup(cli_args):
    group_info = GroupInfo(mva_params.color_by_group, **vars(cli_args))
    shapeSysts = {clean_syst(syst) for syst in get_list_systs(**vars(cli_args))}
    allSysts = [syst for syst in mva_params.systematics
                if syst.name in shapeSysts or syst.syst_type == "lnN"]

    group_list = list(group_info.get_memberMap().keys())
    group_list.remove(cli_args.signal)
    group_list.insert(0, cli_args.signal)

    with Card_Maker(cli_args.workdir/"combine", cli_args.years, group_list, cli_args.fit_var) as card:
        card.write_systematics(allSysts)
