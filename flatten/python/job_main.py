#!/usr/bin/env python3
import pandas as pd
import logging
import uproot

from analysis_suite.commons.configs import get_list_systs, get_inputs, get_ntuple
from analysis_suite.Plotting.plotter import Plotter
from analysis_suite.commons.info import GroupInfo
from analysis_suite.commons.constants import lumi
import analysis_suite.commons.user as user

# from .data_processor import DataProcessor

def setup(cli_args):
    argList = list()

    ntuple = get_ntuple(cli_args.ntuple)
    for year in cli_args.years:
        outdir = cli_args.workdir / year
        outdir.mkdir(exist_ok=True)
        allSysts = get_list_systs(ntuple.get_file(year=year), cli_args.tool, cli_args.systs)
        for syst in allSysts:
            argList.append((cli_args.workdir, outdir, cli_args.ntuple, year, syst))
    return argList


def run(workdir, outdir, tupleName, year, syst):
    inputs = get_inputs(workdir)
    ntuple = get_ntuple(tupleName)

    groups = GroupInfo(inputs.color_by_group).setup_groups()
    plotter = Plotter(ntuple.get_file(year=year), groups, ntuple=ntuple, systName=syst)

    final_set = dict()
    for member, vgs in plotter.dfs.items():
        for tree, vg in vgs.items():
            df_dict = {varname: func(vg) for varname, func in inputs.allvar.items()}
            df_dict["scale_factor"] = vg.scale
            df = pd.DataFrame.from_dict(df_dict)
            df = df.astype({col: int for col in df.columns if col[0] == 'N'})
            if member not in final_set:
                final_set[member] = df
            else:
                final_set[member] = pd.concat([final_set[member], df], ignore_index=True)
            print(f"Finished setting up {member} in tree {tree}")

    with uproot.recreate(outdir / f'processed_{syst}_{ntuple.region}.root') as f:
        for group, df in final_set.items():
            if not len(df):
                continue
            f[group] = df


def cleanup(cli_args):
    pass
