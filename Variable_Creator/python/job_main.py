#!/usr/bin/env python3
import numpy as np
import subprocess

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir, getGroupDict, get_list_systs
from .data_processor import DataProcessor
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    argList = list()
    for year in cli_args.years:
        infile = f'result_{year}.root'
        allSysts = get_list_systs(infile, cli_args.systs)
        for syst in allSysts:
            argList.append((groupDict, infile, cli_args.workdir, year, syst))

    return argList
        

def run(groupDict, infile, workdir, year, syst):
    outdir = f'{workdir}/{year}'
    data = DataProcessor(mva_params.usevar, groupDict, syst)
    checkOrCreateDir(outdir)
    print(f'Processing year {year} MC')
    data.process_year(infile, outdir)


def cleanup(cli_args):
    infiles = [f'{cli_args.workdir}/{year}/train_Nominal.root' for year in cli_args.years ]
    subprocess.run(["hadd", "-f", f"{cli_args.workdir}/train_Nominal.root"] + infiles)
