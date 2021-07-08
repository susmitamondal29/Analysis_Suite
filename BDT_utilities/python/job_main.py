#!/usr/bin/env python3
import logging

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import getGroupDict, get_list_systs

import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    argList = list()
    for year in cli_args.years:
        path = cli_args.workdir / year
        allSysts = get_list_systs(path, cli_args.systs)
        for syst in allSysts:
            argList.append((groupDict, cli_args.workdir, cli_args.train,
                                cli_args.apply_model, year, syst))

    return argList
        

def run(groupDict, workdir, trainType, applyModel, year, systName):
    if trainType == "None":
        from .dataholder import MLHolder
        mvaRunner = MLHolder(mva_params.usevar, groupDict)
    if trainType == "DNN":
        from .DNN import KerasMaker
        mvaRunner = KerasMaker(mva_params.usevar, groupDict)
    elif trainType == "TMVA":
        from .TMVA import TMVAMaker
        mvaRunner = TMVAMaker(mva_params.usevar, groupDict)
    else:
        from .MvaMaker import XGBoostMaker
        mvaRunner = XGBoostMaker(mva_params.usevar, groupDict)
    # mvaRunner.add_cut(mva_params.cuts)

    if applyModel:
        mvaRunner.setup_files(workdir, year)
        mvaRunner.apply_model(workdir)
        mvaRunner.apply_model(workdir, False)

        logging.info(f"Starting to write out for year {year} and syst {systName}")
        mvaRunner.output(workdir, year, systName)
        logging.info(f"Finished writing out for year {year} and syst {systName}")
    elif trainType != "None":
        mvaRunner.setup_files(workdir, train=True)
        fitModel = mvaRunner.train(workdir)
        logging.info("Training finished. To apply training model to code, run code again while applying the model")
        return
    else:
        return
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
    return
