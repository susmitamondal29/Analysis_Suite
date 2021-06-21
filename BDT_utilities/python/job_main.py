#!/usr/bin/env python3
import numpy as np
from pathlib import Path

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir, getGroupDict, get_list_systs
from .MVAPlotter import MVAPlotter
import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))
    groupDict = getGroupDict(mva_params.groups, group_info)

    argList = list()
    for year in cli_args.years:
        path = Path(f"{cli_args.workdir}/{year}")
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

        print(f"Starting to write out for year {year} and syst {systName}")
        mvaRunner.output(workdir, year, systName)
        print(f"Finished writing out for year {year} and syst {systName}")
    elif trainType != "None":
        mvaRunner.setup_files(workdir, train=True)
        fitModel = mvaRunner.train(workdir)
        print("Training finished. To apply training model to code, run code again while applying the model")
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
    lumi = cli_args.lumi*1000
    outDir = f'{cli_args.workdir}/{cli_args.year}'
    # groupMembers = [item for sublist in cli_args.groupDict.values() for item in sublist]
    output = MVAPlotter(outDir, cli_args.groupDict, lumi)
    output.make_roc("Signal", ["Background"], "Background", "SignalvsAll")
    output.plot_all_shapes("NlooseBJets", np.linspace(0, 9, 10), "allGroups")
    output.plot_all_shapes("HT", np.linspace(200, 1750, 31), "allGroups")
    output.plot_all_shapes("JetLep1_Cos", np.linspace(-1, 1, 20), "allGroups")
    output.plot_fom("Signal", ["Background"], "Background", np.linspace(0, 1, 20))


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

