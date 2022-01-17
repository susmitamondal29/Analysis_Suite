#!/usr/bin/env python3
import subprocess
from pathlib import Path
import logging

import analysis_suite.commons.configs as config
from .data_processor import DataProcessor
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    argList = list()
    allSysts = config.get_list_systs(**vars(cli_args))
    trees = config.get_trees(cli_args.years)

    for year in cli_args.years:
        outdir = cli_args.workdir / year
        config.checkOrCreateDir(outdir)
        infile = Path(f'result_{year}.root')
        for tree in trees:
            if tree == "Analyzed":
                for syst in allSysts:
                    argList.append((infile, outdir, tree, year, syst))
            else:
                argList.append((infile, outdir, tree, year, "Nominal"))

    return argList
        

def run(infile, outdir, tree, year, syst):
    data = DataProcessor(mva_params.allvar, syst)
    logging.info(f'Processing year {year} with syst {syst} MC')
    data.process_year(infile, outdir, tree)


def cleanup(cli_args):
    pass
