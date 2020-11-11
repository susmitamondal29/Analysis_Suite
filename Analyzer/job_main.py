#!/usr/bin/env python3

import warnings
import os
import importlib
warnings.filterwarnings('ignore')

from Analyzer import Scheduler
from commons import FileInfo
from commons.configs import checkOrCreateDir

def setup(cli_args):
    analysis_name = "Analyzer."+cli_args.analysis
    MyAnalysis = importlib.import_module(analysis_name)
    Scheduler.jobs = [MyAnalysis.Muon, MyAnalysis.Electron, MyAnalysis.Jet,
                      MyAnalysis.EventWide]
    importlib.import_module("{}.{}_{}".format(analysis_name,
                                              cli_args.analysis,
                                              cli_args.year))
    info = FileInfo(analysis=cli_args.analysis, selection=cli_args.selection)
    
    if len(cli_args.filenames) == 1 and not cli_args.filenames[0]:
        raise Exception("No files given")
    files_dict = info.get_file_dict(cli_args.filenames)
    checkOrCreateDir("{}/masks".format(cli_args.workdir))
    checkOrCreateDir("{}/tmp_masks".format(cli_args.workdir))
    if cli_args.channels:
        MyAnalysis.set_channel(cli_args.channels)
        checkOrCreateDir("{}/{}".format(cli_args.workdir, cli_args.channels))
        
    argList = list()
    redos = set(cli_args.rerun.split(",")) if cli_args.rerun else set()
    for group, files in files_dict.items():
        argList.append((group, files, cli_args.workdir, info.get_xsec(group),
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
