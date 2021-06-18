#!/usr/bin/env python3
import numpy as np
from collections import OrderedDict
import subprocess

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir
from .data_processor import DataProcessor
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = OrderedDict()
    for groupName, samples in mva_params.groups:
        new_samples = list()
        for samp in samples:
            if samp in group_info.group2MemberMap:
                new_samples += group_info.group2MemberMap[samp]
            else:
                new_samples.append(samp)
        groupDict[groupName] = new_samples

    argList = list()
    for year in cli_args.years:
        for syst in cli_args.systs:
            if syst == "Nominal":
                argList.append((groupDict, cli_args.workdir, year, syst))
            else:
                argList.append((groupDict, cli_args.workdir, year, f'{syst}_up'))
                argList.append((groupDict, cli_args.workdir, year, f'{syst}_down'))
    return argList
        

def run(groupDict, workdir, year, syst):
    data = DataProcessor(mva_params.usevar, groupDict, syst)
    checkOrCreateDir(f'{workdir}/{year}')
    print(f'Processing year {year} MC')
    data.process_year(year, workdir)


def cleanup(cli_args):
    infiles = [f'{cli_args.workdir}/{year}/train_Nominal.root' for year in cli_args.years ]
    subprocess.run(["hadd", "-f", f"{cli_args.workdir}/train_Nominal.root"] + infiles)
