#!/usr/bin/env python3

from threading import Thread
from queue import Queue
import multiprocessing as mp
import warnings
import os
import sys
import datetime

from commons.configs import get_cli, checkOrCreateDir
import inputs
warnings.filterwarnings('ignore')


def job_run(func, *args):
    func(*args)

def worker():
    while True:
        func, args = q.get()
        job_run(func, *args)
        q.task_done()


if __name__ == "__main__":
    cli_args = get_cli()
    callTime = str(datetime.datetime.now())
    command = ' '.join(sys.argv)
    argList = list()
    func = None
    parallel = ""
 
    ##############
    # Setup jobs #
    ##############
    checkOrCreateDir(cli_args.workdir)
    if cli_args.tool == "mva":
        from BDT_utilities import job_main
    elif cli_args.tool == "plot":
        from Plotting import job_main
        parallel = "multiprocess"
    elif cli_args.tool == "analyze":
        from Analyzer import job_main
        parallel = "thread"
    argList = job_main.setup(cli_args)
    func = job_main.run
    
    #############
    # Start Job #
    #############
    if cli_args.j == 1 or not parallel:
        [func(*al) for al in argList]
    elif parallel == "multiprocess":
        pool = mp.Pool(args.j)
        pool.map(func, argList)
        pool.close()
    elif parallel == "thread":
        q = Queue()
        for _ in range(cli_args.j):
            t = Thread(target=worker)
            t.daemon = True
            t.start()
        [q.put((func, al)) for al in argList]
        q.join()

    job_main.cleanup(cli_args)
