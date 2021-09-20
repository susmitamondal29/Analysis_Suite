#!/usr/bin/env python3
import subprocess
from pathlib import Path
import logging

from analysis_suite.commons.configs import checkOrCreateDir, get_list_systs
from .data_processor import DataProcessor
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    argList = list()
    allSysts = get_list_systs(**vars(cli_args))

    for year in cli_args.years:
        outdir = cli_args.workdir / year
        checkOrCreateDir(outdir)
        infile = Path(f'result_{year}.root')
        for syst in allSysts:
            argList.append((infile, outdir, year, syst))

    return argList
        

def run(infile, outdir, year, syst):
    data = DataProcessor(mva_params.allvar, syst)
    logging.info(f'Processing year {year} with syst {syst} MC')
    data.process_year(infile, outdir)


def cleanup(cli_args):
    pass
