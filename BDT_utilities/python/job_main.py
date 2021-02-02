#!/usr/bin/env python3
import os
import argparse
import numpy as np
from collections import OrderedDict
import xgboost as xgb

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir
from .MvaMaker import XGBoostMaker
from .MVAPlotter import MVAPlotter
from analysis_suite.data.inputs import mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = OrderedDict()
    for groupName, samples in mva_params.groups:
        new_samples = list()
        for samp in samples:
            if samp in group_info.group2MemberMap:
                new_samples += group_info.group2MemberMap[samp]
            else:
                new_samples.append(samp)
        groupDict[groupName] = new_samples

    outDir ="{}/{}".format(cli_args.workdir, cli_args.channels)
    checkOrCreateDir("{}/test".format(outDir))
    checkOrCreateDir("{}/train".format(outDir))
    cli_args.groupDict = groupDict

    if not cli_args.train:
        return ()
    return ((groupDict, outDir, cli_args.model),)

def run(groupDict, outDir, applyModel):
    mvaRunner = XGBoostMaker(mva_params.usevar, groupDict)
    mvaRunner.add_files("result.root")

    if applyModel:
        fitModel = mvaRunner.apply_model(applyModel)
        impor = fitModel.get_booster().get_score(importance_type= "total_gain")
    elif mva_params.single == True:
        fitModel = mvaRunner.train_single()
        fitModel.save_model("{}/model.bin".format(outDir))
        impor = fitModel.get_score(importance_type= "total_gain")
    else:
        fitModel = mvaRunner.train()
        fitModel.save_model("{}/model.bin".format(outDir))
        impor = fitModel.get_booster().get_score(importance_type= "total_gain")
    mvaRunner.output(outDir)
    sorted_import = {k: v for k, v in sorted(impor.items(), key=lambda item: item[1])}
    import matplotlib.pyplot as plt
    plt.barh(range(len(sorted_import)), list(sorted_import.values()),
                     align='center',
                     height=0.5,)
    plt.yticks(range(len(sorted_import)), sorted_import.keys())
    plt.xlabel("Total Gain")
    plt.title("Variable Importance")
    plt.tight_layout()
    plt.savefig("{}/importance.png".format(outDir))
    plt.close()

def cleanup(cli_args):
    lumi = cli_args.lumi*1000
    outDir ="{}/{}".format(cli_args.workdir, cli_args.channels)
    groupMembers = [item for sublist in cli_args.groupDict.values() for item in sublist]
    output = MVAPlotter(outDir, cli_args.groupDict.keys(), groupMembers, lumi)


    # ttbar = output[output.work_set.groupName == "ttbar"]
    # dy = output[output.work_set.groupName == "DYm50"]
    # dy10 = output[output.work_set.groupName == "DYm10-50"]
    # wjets = output[output.work_set.groupName == "wjets"]
    # tzq = output[output.work_set.groupName == "tzq"]
    # ggh2zz = output[output.work_set.groupName == "ggh2zz"]
    # print(np.unique(output.work_set.groupName))
    # def print_val(name, bkg, ft):
    #     df = output.work_set[output.work_set.groupName == name]
    #     print("Precut {}({}): {:.3f}".format(name, len(df), sum(df.final_factor)))
    #     init = sum(df.final_factor)
    #     if init <= 0:
    #         return
    #     dfcut = df[df["BDT.Background"] > bkg]
    #     dfcut = dfcut[dfcut["BDT.FourTop"] > ft]
    #     print("Postcut {}({}): {:.3f}".format(name, len(dfcut), sum(dfcut.final_factor)))
    #     print("Decrease: {:.1f}%".format(100*sum(dfcut.final_factor)/init))

    # print_val("ttbar", 0.8, 0.15)
    # print_val("DYm50", 0.8, 0.15)
    # print_val("DYm10-50", 0.8, 0.15)
    # print_val("wjets", 0.8, 0.15)
    # print_val("tzq", 0.8, 0.15)
    # print_val("ggh2zz", 0.8, 0.15)

    # output.plot_all_shapes("NlooseBJets", np.linspace(0, 9, 10), "allGroups")
    # output.plot_all_shapes("HT", np.linspace(200, 1750, 31), "allGroups")
    # output.plot_all_shapes("JetLep1_Cos", np.linspace(-1, 1, 20), "allGroups")
    # output.plot_fom("Signal", ['FourTop'], "BDT.FourTop", stobBins, "ft")
    # output.plot_fom("FourTop", ['Signal'], "BDT.FourTop", stobBins, "ft_rev", reverse=True)
    # output.make_roc("Signal", ["FourTop"], "FourTop", "SignalvsAll")
    # output.plot_func("Signal", ["FourTop"], "BDT.Background", stobBins, "onlyFT")
    # output.plot_func("Signal", ["FourTop"], "BDT.FourTop", stobBins, "onlyFT")

    # output.plot_func("Signal", ["FourTop"], "HT", np.linspace(200, 1500, 20), "ft")
    # output.plot_func("Signal", ["FourTop"], "MET", np.linspace(0, 500, 20), "ft")
    # output.plot_func("Signal", ["FourTop"], "centrality", np.linspace(0, 1., 20), "ft")
    # output.plot_func("Signal", ["FourTop"], "sphericity", np.linspace(0, 1., 20), "ft")
    # output.plot_func("Signal", ["FourTop"], "NlooseBJets", np.linspace(0, 10, 10), "ft")
    # output.plot_func("Signal", ["FourTop"], "NtightBJets", np.linspace(0, 5, 5), "ft")

    # output.plot_all_shapes("NJets", np.linspace(0, 15, 16), "allGroups")
    # output.plot_all_shapes("MET", np.linspace(0, 500, 50), "allGroups")
    # output.plot_all_shapes("HT", np.linspace(0, 1500, 50), "allGroups")
    # output.plot_func("Signal", ["Background"], "BDT.Background", stobBins)
    # output.plot_fom("Signal", ["Background"], "BDT.Background", stobBins)
    # output.plot_fom("Signal", ["Background"], "BDT.Background", stobBins)
    # print(max(output.get_fom("Signal", ["Background", "FourTop"], "BDT.Background",
    #                      stobBins)))
    # output.plot_fom("Signal", ['FourTop', "Background"], "BDT.Background", stobBins, "beforeCut")
    # output.apply_cut("BDT.Background>0.8")
    # output.apply_cut("BDT.FourTop>0.15")
    # output.plot_fom("Signal", ['FourTop', "Background"], "BDT.Background", stobBins, "afterCut")
    # output.write_out("postselection")
    # if not single:
    #     # output.plot_all_shapes("BDT.FourTop", stobBins)
    # maxSBVal = output.plot_fom_2d("FourTop", "BDT.Background", "BDT.FourTop",
    #                                   stob2d, stob2d)
    # print(maxSBVal)
    #     # output.plot_func_2d("Signal", "BDT.Background", "BDT.FourTop",
    #     #             stob2d, stob2d, "Signal", lines=maxSBVal[1:])
    #     # output.plot_func_2d("Background", "BDT.Background", "BDT.FourTop",
    #     #             stob2d, stob2d, "Background", lines=maxSBVal[1:])
    #     output.plot_func_2d("FourTop", "BDT.Background", "BDT.FourTop",
    #                 stob2d, stob2d, "FourTop", lines=maxSBVal[1:])
    #     print("FourTop: ", output.approx_likelihood("Signal", ["Background", "FourTop"],
    #                                         "BDT.FourTop", stobBins))
    #     print("Background: ", output.approx_likelihood("Signal", ["Background", "FourTop"],
    #                                            "BDT.Background", stobBins))



        # output.plot_all_shapes("BDT.FourTop", stob2d, "post_allGroups")
    # output.plot_func("Signal", ["Background"], "HT", np.linspace(0, 1500, 50), "func")
    # output.plot_func("Signal", ["FourTop"], "BDT.Background", stobBins, extra_name="bkg_compare")
    # output.plot_func("Signal", ["FourTop"], "BDT.FourTop", stobBins, extra_name="ft_compare")

    # output.print_info("BDT.Background", groupMembers)
    # output.apply_cut("BDT.FourTop>0.2")
    #
    # output.print_info("BDT.Background", groupMembers)
    # output.write_out("postselection")
# gSet = output.get_sample()

# output.make_roc("Signal", ["FourTop", "Background"], "Signal", "SignalvsAll")

# print("FourTop: ", output.approx_likelihood("Signal", ["Background", "FourTop"],
#                                             "BDT.FourTop", stobBins))
# print("Background: ", output.approx_likelihood("Signal", ["Background", "FourTop"],
#                                                "BDT.Background", stobBins))
# output.apply_cut("BDT.FourTop>{}".format(maxSBVal[2]))
# output.apply_cut("BDT.Background>{}".format(maxSBVal[1]))
# output.write_out("postSelection_BDT.2020.06.03_SignalSingle")
