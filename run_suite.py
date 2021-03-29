#!/usr/bin/env python3

from threading import Thread
from queue import Queue
import multiprocessing as mp
import warnings
import os
import sys
import datetime
import logging

from analysis_suite.commons.configs import get_cli, checkOrCreateDir
warnings.filterwarnings('ignore')


def job_run(func, *args):
    func(*args)

if __name__ == "__main__":
    cli_args = get_cli()
    logging.basicConfig(level=getattr(logging, cli_args.log, None))
    callTime = str(datetime.datetime.now())
    command = ' '.join(sys.argv)
    argList = list()
    func = None

    ##############
    # Setup jobs #
    ##############

    if cli_args.tool == "mva":
        from analysis_suite.BDT_utilities import job_main
    elif cli_args.tool == "plot":
        from analysis_suite.Plotting import job_main
        
    argList = job_main.setup(cli_args)
    func = job_main.run

    #############
    # Start Job #
    #############
    if cli_args.j == 1:
        [func(*al) for al in argList]
    else:
        pool = mp.Pool(args.j)
        pool.map(func, argList)
        pool.close()

    job_main.cleanup(cli_args)
