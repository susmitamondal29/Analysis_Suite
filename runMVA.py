#!/usr/bin/env python
import os
import argparse
import numpy as np
from collections import OrderedDict
import xgboost as xgb

from commons import FileInfo
import commons.configs as config
from bdt_utils.MvaMaker import XGBoostMaker
from bdt_utils.MVAPlotter import MVAPlotter

##################
# User Variables #
##################

single=True

# Variables used in Training
usevar = {
    "NJets": "num('Jets/Jet_pt')",
    "NBJets": "num('BJets/Jet_pt')",
    "NlooseBJets": "num_mask('Event_masks/Jet_looseBjetMask')",
    "NtightBJets": "num_mask('Event_masks/Jet_tightBjetMask')",
    "NlooseLeps": "num('looseLeptons/Lepton_pt')",
    "HT": "var('Event_variables/Event_HT')",
    "MET": "var('Event_MET/MET_pt')",
    "centrality": "var('Event_variables/Event_centrality')",
    "sphericity": "var('Event_variables/Event_sphericity')",
    "j1Pt": "nth('Jets/Jet_pt', 0)",
    "j2Pt": "nth('Jets/Jet_pt', 1)",
    "j3Pt": "nth('Jets/Jet_pt', 2)",
    "j4Pt": "nth('Jets/Jet_pt', 3)",
    "j5Pt": "nth('Jets/Jet_pt', 4)",
    "j6Pt": "nth('Jets/Jet_pt', 5)",
    "j7Pt": "nth('Jets/Jet_pt', 6)",
    "j8Pt": "nth('Jets/Jet_pt', 7)",
    "b1Pt": "nth('BJets/Jet_pt', 0)",
    "b2Pt": "nth('BJets/Jet_pt', 1)",
    "b3Pt": "nth('BJets/Jet_pt', 2)",
    "b4Pt": "nth('BJets/Jet_pt', 3)",
    "l1Pt": "nth('tightLeptons/Lepton_pt', 0)",
    "l2Pt": "nth('tightLeptons/Lepton_pt', 1)",
    "lepMass" : "mass('tightLeptons/Lepton', 0, 'tightLeptons/Lepton', 1)",
    "lepDR" : "dr('tightLeptons/Lepton', 0, 'tightLeptons/Lepton', 1)",
    "jetDR" : "dr('Jets/Jet', 0, 'Jets/Jet', 1)",
    "jetMass" : "mass('Jets/Jet', 0, 'Jets/Jet', 1)",
    "LepCos" : "cosDtheta('tightLeptons/Lepton', 0, 'tightLeptons/Lepton', 1)",
    "JetLep1_Cos" : "cosDtheta('tightLeptons/Lepton', 0, 'Jets/Jet', 0)",
    "JetLep2_Cos" : "cosDtheta('tightLeptons/Lepton', 1, 'Jets/Jet', 0)",
}

#usevar = [ "Shape1", "Shape2","JetBJet_DR",  "JetBJet_Cos"


# Input Rootfile
INPUT_TREE = "inputTrees_new.root"

# Sampels and the groups they are a part of
if single:
    groups = [["Signal", ["ttt_201X"]],
              ["Background", ["ttw", "ttz", "tth", "ttXY", "vvv", "vv","xg" "4top2016","other"]]]
else:
    groups = [["Signal", ["ttt_201X"]],
              ["FourTop", ["4top2016",]],
              ["Background", ["ttw", "ttz", "tth", "ttXY", "vvv", "vv", "xg","other"]]] #

def get_com_args():
    parser = config.get_generic_args()
    parser.add_argument('-t', '--train', action="store_true",
                        help="Run the training")
    parser.add_argument("-i", "--indir", type=str, required=True,
                        help="Input root file (output of makeHistFile.py)")
    parser.add_argument("-m", "--model", type=str, default="",
                        help="Model file")
    return parser.parse_args()


def train(args, groupDict):
    mvaRunner = XGBoostMaker(usevar)
    for groupName, samples in groupDict.items():
        mvaRunner.add_group(groupName, samples, args.indir, args.channels)
        
    if args.model:
        mvaRunner.apply_model(args.model)
    elif single == True:
        fitModel = mvaRunner.train_single()
        fitModel.save_model("{}/model.bin".format(args.outdir))
        impor = fitModel.get_score(importance_type= "total_gain")
    else:
        fitModel = mvaRunner.train()
        fitModel.save_model("{}/model.bin".format(args.outdir))
        impor = fitModel.get_booster().get_score(importance_type= "total_gain")
    mvaRunner.output(args.outdir)

    # sorted_import = {k: v for k, v in sorted(impor.items(), key=lambda item: item[1])}
    # import matplotlib.pyplot as plt
    # plt.barh(range(len(sorted_import)), list(sorted_import.values()),
    #                  align='center',
    #                  height=0.5,)
    # plt.yticks(range(len(sorted_import)), sorted_import.keys())
    # plt.xlabel("Total Gain")
    # plt.title("Variable Importance")
    # plt.tight_layout()
    # plt.savefig("{}/importance.png".format(args.outdir))
    # plt.close()


    
def get_group_dict(groups):
    groupDict = OrderedDict()
    for groupName, samples in groups:
        new_samples = list()
        for samp in samples:
            if samp in file_info.group2MemberMap:
                new_samples += file_info.group2MemberMap[samp]
            else:
                new_samples.append(samp)
        groupDict[groupName] = new_samples
    return groupDict

        
if __name__ == "__main__":
    args = get_com_args()
    file_info = FileInfo(**vars(args))
    groupDict = get_group_dict(groups)
    groupMembers = [item for sublist in groupDict.values() for item in sublist]
    lumi = args.lumi*1000
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)
        os.mkdir("{}/test".format(args.outdir))
        os.mkdir("{}/train".format(args.outdir))

    if args.train or args.model:
        train(args, groupDict)

    NBINS_2D = 40
    stob2d = np.linspace(0.0, 1.0, NBINS_2D + 1)
    stobBins = np.linspace(0.0, 1, 25)
    
    output = MVAPlotter(args.outdir, groupDict.keys(), groupMembers, lumi)
    output.plot_fom("Signal", ["Background"], "BDT.Background", stobBins)


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
