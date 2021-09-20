#!/usr/bin/env python3
import logging
import numpy as np
import os

from analysis_suite.commons import GroupInfo, PlotInfo
from analysis_suite.commons.configs import getGroupDict, get_list_systs

import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    os.environ["NUMEXPR_MAX_THREADS"] = "8"

    argList = list()

    for syst in get_list_systs(**vars(cli_args)):
        argList.append((groupDict, cli_args.workdir, cli_args.train,
                        cli_args.apply_model, cli_args.years, syst, cli_args.save))

    return argList


def run(groupDict, workdir, trainType, applyModel, years, systName, save_train):
    print(f"Training for syst {systName}")
    if trainType == "XGB":
        from .MvaMaker import XGBoostMaker
        params = {"max_depth": 2, "colsample_by_tree": 0.65, "min_childweight": 1e-3,
                  "subsample": 0.75, "eta": 0.05, "eval_metric": "rmse"}
        mvaRunner = XGBoostMaker(mva_params.usevars, groupDict, systName=systName,
                                 params=params)
    elif trainType == "DNN":
        from .DNN import KerasMaker
        mvaRunner = KerasMaker(mva_params.usevars, groupDict, systName=systName)
    elif trainType == "TMVA":
        from .TMVA import TMVAMaker
        mvaRunner = TMVAMaker(mva_params.usevars, groupDict, systName=systName)
    else:

        return
    # mvaRunner.add_cut(mva_params.cuts)

    for year in years:
        mvaRunner.setup_year(workdir, year, save_train)

    if not applyModel:
        mvaRunner.train(workdir)

    for year in years:
        mvaRunner.apply_model(workdir, year)
        # for i in np.linspace(0, 1, 11):
        #     mvaRunner.get_stats(year, i)
        # logging.info(f"Starting to write out for year {year} and syst {systName}")
        mvaRunner.output(workdir, year)
        # logging.info(f"Finished writing out for year {year} and syst {systName}")


    # sorted_import = {k: v for k, v in sorted(impor.items(), key=lambda item: item[1])}
    # import matplotlib.pyplot as plt
    # plt.barh(range(len(sorted_import)), list(sorted_import.values()),
    #                  align='center',
    #                  height=0.5,)
    # plt.yticks(range(len(sorted_import)), sorted_import.keys())
    # plt.xlabel("Total Gain")
    # plt.title("Variable Importance")
    # plt.tight_layout()
    # plt.savefig("{}/importance.png".format(outDir))
    # plt.close()

def cleanup(cli_args):
    if not cli_args.plot:
        return

    from .MVAPlotter import MVAPlotter
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    plot_info = PlotInfo(cli_args.info)

    plots = [
        MVAPlotter(groupDict, "test", "Nominal", **vars(cli_args)),
        # MVAPlotter(groupDict, "train", "Nominal", **vars(cli_args)),
    ]


    for plot in plots:
        year = "2016"
        cut = 0.6
        plot.apply_cut(f"Signal>{cut}", year)

        # for year in cli_args.years:
        #     plot.make_roc(year)
        #     # plot.group_shapes("Signal", np.linspace(0, 1, 26), year)
        #     plot.plot_fom("Signal", np.linspace(0, 1, 26), year)

        # plot.make_roc("2016")
        plot.group_shapes("Signal", np.linspace(0, 1, 26), "2016")
        # plot.plot_fom("Signal", np.linspace(0, 1, 26), "2016")

        # for plot_name in plot_list:
        #     bins = plot_info.get_binning(plot_name).edges
        #     # plot.year_shapes(usevar, bins, "Signal")
        #     # plot.year_shapes(usevar, bins, "Background")
        #     plot.group_shapes(plot_name, bins, "2016")


        # for usevar in mva_params.usevars.keys():
        #     print(usevar)
        #     bins = plot_info.get_binning(usevar).edges
        #     # plot.year_shapes(usevar, bins, "Signal")
        #     # plot.year_shapes(usevar, bins, "Background")
        #     plot.group_shapes(usevar, bins, year)

    pass
#    plotter.func("NJets", np.linspace(0, 15, 15), "2016")

    # for year in cli_args.years:
    #     plotter.print_info("NJets", year)
    # for year in cli_args.years:
    #     plotter.print_info("NBJets", year)
