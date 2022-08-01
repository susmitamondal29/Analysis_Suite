#!/usr/bin/env python3
import logging

import analysis_suite.commons.configs as config
from analysis_suite.commons.info import PlotInfo
import analysis_suite.data.inputs as mva_params
import analysis_suite.commons.user as user

from .data_processor import DataProcessor

def setup(cli_args):
    argList = list()

    for year in cli_args.years:
        outdir = cli_args.workdir / year
        config.checkOrCreateDir(outdir)
        infile = user.hdfs_area / f'workspace/signal_region/{year}'
        trees = mva_params.trees
        allSysts = config.get_list_systs(infile, args.tool)
        for outname, tree in trees.items():
            for syst in allSysts:
                argList.append((infile, outdir, outname, tree, year, syst))
    return argList
        

def run(infile, outdir, outname, trees, year, syst):
    data = DataProcessor(mva_params.allvar, PlotInfo.lumi[year], syst)
    logging.info(f'Processing year {year} with syst {syst} MC')
    if isinstance(trees, list):
        for tree in trees:
            data.process_year(infile, tree)
    else:
        data.process_year(infile, trees)
    if data:
        data.write_out(outdir / f'processed_{syst}_{outname}.root')


def cleanup(cli_args):
    pass
