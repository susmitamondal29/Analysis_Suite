#!/usr/bin/env python3
import subprocess
from pathlib import Path
import logging

import analysis_suite.commons.configs as config
from analysis_suite.commons.info import PlotInfo
from .data_processor import DataProcessor
import analysis_suite.data.inputs as mva_params
import analysis_suite.commons.user as user

def setup(cli_args):
    argList = list()
    allSysts = config.get_list_systs(**vars(cli_args))
    workdir = user.workspace_area / cli_args.workdir

    for year in cli_args.years:
        outdir = workdir / year
        config.checkOrCreateDir(outdir)
        infile = user.hdfs_area / f'workspace/signal_region/{year}'
        trees = mva_params.trees
        for outname, tree in trees.items():
            for syst in allSysts:
                argList.append((infile, outdir, outname, tree, year, syst))
    return argList
        

def run(infile, outdir, outname, trees, year, syst):
    data = DataProcessor(mva_params.allvar, PlotInfo.lumi[year], syst)
    logging.info(f'Processing year {year} with syst {syst} MC')
    if isinstance(trees, list):
        for tree in trees:
            data.process_year(infile, outdir, tree)
    else:
        data.process_year(infile, outdir, trees)

    data.write_out(outdir / f'processed_{syst}_{outname}.root')


def cleanup(cli_args):
    pass
