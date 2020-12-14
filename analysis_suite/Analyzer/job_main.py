#!/usr/bin/env python3

import warnings
import os
import importlib
warnings.filterwarnings('ignore')

from .Scheduler import Scheduler
from analysis_suite.commons import BasicInfo, FileInfo
from analysis_suite.commons.configs import checkOrCreateDir

def setup(cli_args):
    analysis_name = "analysis_suite.Analyzer."+cli_args.analysis
    MyAnalysis = importlib.import_module(analysis_name)
    Scheduler.jobs = [MyAnalysis.Muon, MyAnalysis.Electron, MyAnalysis.Jet,
                      MyAnalysis.EventWide]
    importlib.import_module("{}.{}_{}".format(analysis_name,
                                              cli_args.analysis,
                                              cli_args.year))
    if len(cli_args.filenames) == 1 and not cli_args.filenames[0]:
        raise Exception("No files given")

    files_dict = dict()
    if cli_args.workdir == ".":
        group = cli_args.filenames[0]
        info = BasicInfo(mcPath="montecarlo_2016.py")
        files_dict[group] = ("./*.root", info.get_xsec(group))
    else:
        info = FileInfo(analysis=cli_args.analysis, selection=cli_args.selection)
        files_dict = info.get_file_dict_with_xsec(cli_args.filenames)

    checkOrCreateDir("{}/masks".format(cli_args.workdir))
    if cli_args.channels:
        MyAnalysis.set_channel(cli_args.channels)
        checkOrCreateDir("{}/{}".format(cli_args.workdir, cli_args.channels))
    
    argList = list()
    redos = set(cli_args.rerun.split(",")) if cli_args.rerun else set()
    for group, (files, xsec) in files_dict.items():
        argList.append((group, files, cli_args.workdir, xsec,
                        cli_args.channels, redos))

    for arg in argList[::-1]:
        print(arg[0])
    print()
    
    return argList


def run(group, files, out_dir, xsec, chan, redos):
    job = Scheduler(group, files, out_dir, xsec)
    job.run(redos)
    job.apply_mask(chan)


def cleanup(cli_args):
    pass
