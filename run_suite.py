#!/usr/bin/env python3
import multiprocessing as mp
import warnings
import logging

from analysis_suite.commons.configs import get_cli
warnings.filterwarnings('ignore')

if __name__ == "__main__":
    cli_args = get_cli()
    logging.basicConfig(level=getattr(logging, cli_args.log, None))

    ##############
    # Setup jobs #
    ##############

    if cli_args.tool == "mva":
        from analysis_suite.BDT_utilities import job_main
    elif cli_args.tool == "plot":
        from analysis_suite.Plotting import job_main
    elif cli_args.tool == "analyze":
        from analysis_suite.Variable_Creator import job_main
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
