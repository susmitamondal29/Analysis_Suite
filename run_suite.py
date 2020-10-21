#!/usr/bin/env python3

from threading import Thread
from queue import Queue
import multiprocessing as mp
import warnings
import os
import sys
import datetime

from commons import configs
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
    cli_args = configs.get_cli()
    callTime = str(datetime.datetime.now())
    command = ' '.join(sys.argv)
    argList = list()
    func = None
    parallel_tool = ""

    ##############
    # Setup jobs #
    ##############
    if cli_args.tool == "mva":
        pass
    elif cli_args.tool == "plot":
        from Plotting import job_main
        parallel = "multiprocess"
    elif cli_args.tool == "analyze":
        parallel = "thread"
        exit()
    argList = job_main.setup(cli_args)
    func = job_main.run

    #############
    # Start Job #
    #############
    if cli_args.j == 1 or not parallel_tool:
        [job_run(func, *al) for al in argList]
    elif parallel_tool == "multiprocess":
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
