#!/usr/bin/env python3
import multiprocessing as mp
import warnings
import logging

from analysis_suite.commons.configs import get_cli, setup
warnings.filterwarnings('ignore')

if __name__ == "__main__":
    cli_args = get_cli()
    setup(cli_args)
    logging.basicConfig(level=getattr(logging, cli_args.log, None))

    ##############
    # Setup jobs #
    ##############

    if cli_args.tool == "mva":
        from analysis_suite.machine_learning import job_main
    elif cli_args.tool == "plot":
        from analysis_suite.plotting import job_main
    elif cli_args.tool == "flatten":
        from analysis_suite.flatten import job_main
    elif cli_args.tool == "combine":
        from analysis_suite.Combine import job_main
    else:
        exit()


    argList = job_main.setup(cli_args)
    func = job_main.run

    #############
    # Start Job #
    #############
    if cli_args.j == 1:
        [func(*al) for al in argList]
    else:
        with mp.Pool(cli_args.j) as pool:
            pool.starmap(func, argList)

    job_main.cleanup(cli_args)
