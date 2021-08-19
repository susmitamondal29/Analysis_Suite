#!/usr/bin/env python3
import subprocess
from pathlib import Path
import logging

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir, getGroupDict, get_list_systs
from .data_processor import DataProcessor
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    argList = list()
    for year in cli_args.years:
        outdir = cli_args.workdir / year
        checkOrCreateDir(outdir)
        infile = Path(f'result_{year}.root')
        allSysts = get_list_systs(infile, cli_args.systs)
        for syst in allSysts:
            argList.append((groupDict, infile, outdir, year, syst))

    return argList
        

def run(groupDict, infile, outdir, year, syst):
    data = DataProcessor(mva_params.allvar, groupDict, syst)
    logging.info(f'Processing year {year} with syst {syst} MC')
    data.process_year(infile, outdir)


def cleanup(cli_args):
    for type_name in ["train", "test"]:
        infiles = [cli_args.workdir / year / f'{type_name}_Nominal.root' for year in cli_args.years ]
        subprocess.run(["hadd", "-f", cli_args.workdir / f"{type_name}_Nominal.root"] + infiles)
