#!/usr/bin/env python3
import logging

from analysis_suite.commons.configs import get_list_systs, get_inputs
from analysis_suite.commons.constants import lumi
import analysis_suite.commons.user as user

from .data_processor import DataProcessor

def setup(cli_args):
    argList = list()

    tuple_info = get_inputs(cli_args.workdir).tuple_info
    for year in cli_args.years:
        outdir = cli_args.workdir / year
        outdir.mkdir(exist_ok=True)
        infile = user.hdfs_area / f'workspace/signal_region/{year}'
        allSysts = ['Nominal']
        # allSysts = get_list_systs(infile, cli_args.tool)
        for syst in allSysts:
            argList.append((infile, outdir, cli_args.outname, tuple_info, year, syst))
    return argList
        

def run(infile, outdir, outname, tuple_info, year, syst):
    allvar = get_inputs(outdir.parent).allvar
    cuts = tuple_info["tree_cuts"][outname]
    trees = tuple_info["trees"]
    change_name = tuple_info['change_name']
    data = DataProcessor(allvar, lumi[year], systName=syst, cut=cuts, change_name=change_name)
    logging.info(f'Processing year {year} with syst {syst} in CR {outname}')

    for tree in trees:
        data.process_year(infile, tree)
    if data:
        data.write_out(outdir / f'processed_{syst}_{outname}.root')


def cleanup(cli_args):
    pass
