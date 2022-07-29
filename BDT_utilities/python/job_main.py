#!/usr/bin/env python3
import logging
import numpy as np
import os
from importlib import import_module

from analysis_suite.commons import GroupInfo, PlotInfo
from analysis_suite.commons.configs import getGroupDict, get_list_systs
import analysis_suite.commons.user as user
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    os.environ["NUMEXPR_MAX_THREADS"] = "8"

    argList = list()
    allSysts = get_list_systs(cli_args.workdir, 'mva')

    for region in cli_args.regions:
        for syst in allSysts:
            argList.append((groupDict, cli_args.workdir, cli_args.train, cli_args.apply_model,
                            cli_args.years, region, syst, cli_args.save))

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


def run(groupDict, workdir, trainType, applyModel, years, region, systName, save_train):
    mvaRunner = get_mva_runner(trainType)(mva_params.usevars, groupDict, region=region, systName=systName)
    if mvaRunner is None:
        return
    elif trainType == "XGB":
        # best fom
        # params = {"max_depth": 1, "colsample_bytree": 1.0, "min_child_weight": 3.1622776601683795e-05,
        #           "subsample": 1.0, "eta": 0.05, "eval_metric": "rmse"}
         # best likelihood
        params = {"max_depth": 2, "colsample_bytree": 1.0, "min_child_weight": 0.03162277660168379,
                  "subsample": 0.5, "eta": 0.05, "eval_metric": "auc"}
        mvaRunner.update_params(params)

    # mvaRunner.add_cut(mva_params.cuts) # Only used in CutBased for now

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
    pass
