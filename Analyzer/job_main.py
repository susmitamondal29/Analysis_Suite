#!/usr/bin/env python3

import warnings
import os
import importlib
warnings.filterwarnings('ignore')

from Analyzer import Scheduler, CutApplier
from commons import FileInfo
from commons.configs import checkOrCreateDir

def setup(cli_args):
    analysis_name = "Analyzer."+cli_args.analysis
    MyAnalysis = importlib.import_module(analysis_name)
    importlib.import_module("{}.{}_{}".format(analysis_name,
                                              cli_args.analysis,
                                              cli_args.year))
    info = FileInfo(analysis=cli_args.analysis, selection=cli_args.selection)
    files_dict = info.get_file_dict(cli_args.filenames)
    checkOrCreateDir(cli_args.outdir)
    if cli_args.channel:
        MyAnalysis.set_channel(cli_args.channel)
        checkOrCreateDir("{}/{}".format(cli_args.outdir, cli_args.channel))

    argList = list()
    i = 0
    for group, files in files_dict.items():
        mask_exists = os.path.isfile("{}/{}.parquet".format(cli_args.outdir, group))
        if cli_args.proc_type == "apply" and not mask_exists:
            print("Mask file doesn't exist, please create!")
            exit(1)
        elif cli_args.proc_type == "create" and not cli_args.r and mask_exists:
            continue
        i += 1
        argList.append((cli_args.proc_type, cli_args.channel, group, files,
                        cli_args.outdir, info.get_xsec(group), i))
    return argList


def run(group, files, out_dir, xsec, line_diff, chan):
    job = Scheduler(group, files, out_dir, xsec, line_diff)
    job.run()
    job.add_tree()
    job.apply_mask(chan)
    pass

def cleanup(cli_args):
    pass
