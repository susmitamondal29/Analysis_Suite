#!/usr/bin/env python3
import logging
import numpy as np
import os
from importlib import import_module

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


def get_mva_runner(trainType):
    pkg = "analysis_suite.BDT_utilities"
    if trainType == "XGB":
        return import_module(".XGBoost", pkg).XGBoostMaker
    elif trainType == "DNN":
        return import_module(".DNN", pkg).KerasMaker
    elif trainType == "TMVA":
        return import_module(".TMVA", pkg).TMVAMaker
    elif trainType == "CutBased":
        return import_module(".CutBased", pkg).CutBasedMaker
    else:
        return lambda *args, **kwargs : None

def run(groupDict, workdir, trainType, applyModel, years, systName, save_train):
    mvaRunner = get_mva_runner(trainType)(mva_params.usevars, groupDict, systName=systName)
    if mvaRunner is None:
        return
    elif trainType == "XGB":
        # params = {"max_depth": 2, "colsample_by_tree": 1.0, "min_childweight": 1e-3,
        #           "subsample": 0.75, "eta": 0.05, "eval_metric": "error"}
        # params = {"max_depth": 1, "colsample_by_tree": 1.0, "min_childweight": 1e-2,
        #           "subsample": 0.75, "eta": 0.1, "eval_metric": "rmse"}
        # params = {"max_depth": 1, "colsample_by_tree": 1.0, "min_childweight": 0.03,
        #            "subsample": 1.0, "eta": 0.1, "eval_metric": "rmse"}
        # params = {"max_depth": 2, "colsample_by_tree": 1.0, "min_childweight": 3.1622776601683795e-05,
        #            "subsample": 0.625, "eta": 0.1, "eval_metric": "rmse"}

        # best fom
        params = {"max_depth": 1, "colsample_bytree": 1.0, "min_child_weight": 3.1622776601683795e-05,
                  "subsample": 1.0, "eta": 0.05, "eval_metric": "rmse"}
         # best likelihood
        # params = {"max_depth": 2, "colsample_bytree": 1.0, "min_child_weight": 0.03162277660168379,
        #           "subsample": 0.5, "eta": 0.05, "eval_metric": "auc"}


        mvaRunner.update_params(params)

    mvaRunner.add_cut(mva_params.cuts) # Only used in CutBased for now

    print(f"Training for syst {systName}")


    for year in years:
        mvaRunner.setup_year(workdir, year, save_train)

    if not applyModel:
        mvaRunner.train(workdir)

    for year in years:
        if trainType == "XGB":
            mvaRunner.get_importance(workdir)

        mvaRunner.apply_model(workdir, year)
        # for i in np.linspace(0, 1, 11):
        #     mvaRunner.get_stats(year, i)
        logging.info(f"Starting to write out for year {year} and syst {systName}")
        if year == "2016":
            mvaRunner.output(workdir, year)
        logging.info(f"Finished writing out for year {year} and syst {systName}")


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
        # cut = plot.get_max_fom("Signal", np.linspace(0, 1, 201), year)
        plot_name="Signal"
        bins = plot_info.get_binning(plot_name).edges
        print(plot.approx_likelihood(plot_name, bins, year))
        plot.plot_fom(plot_name, bins, "2016", xlabel=plot_info.get_label(plot_name))
        return
        # print(cut)

        # plot.apply_cut(f"Signal>{cut}", year)
        # plot.apply_cut("NlooseBJets>2", year)
        # plot.apply_cut("NJets>3", year)
        # plot.a
        # plot_list = ["HT", "JetLep1_Cos", "NlooseBJets", "NtightBJets", "JetLep2_Cos",
        #              "NlooseMuons", "NBJets", "HT_b", "NJets", "lepDR"]
        # for plot_name in plot_list:
        #     bins = plot_info.get_binning(plot_name).edges
        #  print(f"{plot_name}: {plot.approx_likelihood(plot_name, bins, year)}")
        #     plot.plot_fom(plot_name, bins, "2016", xlabel=plot_info.get_label(plot_name))
        #
        #

        for year in cli_args.years:
            print()
            plot.make_roc(year)
            # plot.group_shapes("Signal", np.linspace(0, 1, 26), year)

            plot.plot_fom("Signal", np.linspace(0, 1, 26), year)

        # plot.make_roc("2016")
        # plot.group_shapes("Signal", np.linspace(0, 1, 26), "2016")
        # plot.plot_fom("Signal", np.linspace(0, 1, 26), "2016")

        # for plot_name in plot_list:
        #     bins = plot_info.get_binning(plot_name).edges
        #     # plot.year_shapes(usevar, bins, "Signal")
        #     # plot.year_shapes(usevar, bins, "Background")
        #     plot.group_shapes(plot_name, bins, "2016")
        # bins = plot_info.get_binning("NBJets").edges
        # for i in np.linspace(0, 1, 20):
        #     plot.apply_cut(f"Signal>{i}", year)
        #     print(f"cut {i}: {plot.approx_likelihood('NBJets', bins, year)}")

        # for usevar in mva_params.usevars.keys():
        #     if "Disc" in usevar:
        #         continue
        #     bins = plot_info.get_binning(usevar).edges
        #     print(f"{usevar}: ")
            # plot.plot_fom(usevar, bins, "2016", xlabel=plot_info.get_label(usevar),
            #               isDisc=plot_info.at(usevar, "Discrete"))
            # print(f"{usevar}: {plot.approx_likelihood(usevar, bins, year)}")
            # plot.year_shapes(usevar, bins, "Signal")
            # plot.year_shapes(usevar, bins, "Background")
            # plot.group_shapes(usevar, bins, year)

    pass
#    plotter.func("NJets", np.linspace(0, 15, 15), "2016")

    # for year in cli_args.years:
    #     plotter.print_info("NJets", year)
    # for year in cli_args.years:
    #     plotter.print_info("NBJets", year)
