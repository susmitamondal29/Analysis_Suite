#!/usr/bin/env python3
import logging
import numpy as np
import os
from importlib import import_module

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import get_list_systs, get_inputs
import analysis_suite.commons.user as user

def setup(cli_args):
    inputs = get_inputs(cli_args.workdir)
    ginfo = GroupInfo(inputs.color_by_group)
    groupDict = {cls_name: ginfo.setup_members(samples) for cls_name, samples in inputs.groups.items()}

    os.environ["NUMEXPR_MAX_THREADS"] = "8"

    argList = list()
    allSysts = get_list_systs(cli_args.workdir, cli_args.tool, cli_args.systs)
    for year in cli_args.years:
        for region in cli_args.regions:
            for syst in allSysts:
                argList.append((groupDict, inputs.usevars, cli_args.workdir, cli_args.model,
                                cli_args.train, year, region, syst, cli_args.save))

    return argList


def run(groupDict, usevars, workdir, model, train, year, region, systName, save_train):
    module = import_module(f'.{model}', "analysis_suite.BDT_utilities")
    maker = getattr(module, next(filter(lambda x : "Maker" in x, dir(module))))
    ml_runner = maker(usevars, groupDict, region=region, systName=systName)

    print(f"Training for syst {systName}")

    if train:
        if model == 'XGBoost':
            # best fom
            # params = {"max_depth": 1, "colsample_bytree": 1.0, "min_child_weight": 3.1622776601683795e-05,
            #           "subsample": 1.0, "eta": 0.05, "eval_metric": "rmse"}
             # best likelihood
            params = {"max_depth": 2, "colsample_bytree": 1.0, "min_child_weight": 0.03162277660168379,
                      "subsample": 0.5, "eta": 0.05, "eval_metric": "auc"}
        elif model == 'CutBased':
            pass
            # mvaRunner.add_cut(mva_params.cuts) # Only used in CutBased for now
        ml_runner.update_params(params)
        # Setup test/train/validate sets
        ml_runner.setup_year(workdir, year, save_train)

        ml_runner.train(workdir)
        ml_runner.get_importance(workdir)
    else:
        ml_runner.read_in_file(workdir, year)
        if not ml_runner: return
    # Apply to test sets and save
    ml_runner.apply_model(workdir, year, get_auc=(systName=="Nominal"))
    ml_runner.output(workdir, year)


def cleanup(cli_args):
    pass
