#!/usr/bin/env python3
import logging

from analysis_suite.commons.configs import get_list_systs, get_inputs, get_ntuple, get_shape_systs
from analysis_suite.commons.constants import lumi
import analysis_suite.commons.user as user

from .data_processor import DataProcessor

def setup(cli_args):
    argList = list()

    ntuple = get_ntuple(cli_args.ntuple)
    for year in cli_args.years:
        outdir = cli_args.workdir / year
        outdir.mkdir(exist_ok=True)
        allSysts = get_list_systs(ntuple.get_file(year=year), cli_args.tool)
        for syst in allSysts:
            argList.append((cli_args.workdir, outdir, cli_args.ntuple, year, syst))
    return argList
        

def run(workdir, outdir, tupleName, year, syst):
    allvar = get_inputs(workdir).allvar
    tuple_info = get_ntuple(tupleName)

    data = DataProcessor(allvar, lumi[year], tuple_info, systName=syst)
    logging.info(f'Processing year {year} with syst {syst} in CR {tuple_info.region}')

    for tree in tuple_info.trees:
        data.process_year(tuple_info.get_file(year=year), tree)
    if data:
        data.write_out(outdir / f'processed_{syst}_{tuple_info.region}.root')


def cleanup(cli_args):
    pass
