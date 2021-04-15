#!/usr/bin/env python3

"""
.. module:: XGBoostMaker
   :synopsis: Takes in ROOT file to run a BDT training over it using XGBoost
.. moduleauthor:: Dylan Teague
"""
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
import xgboost as xgb
from analysis_suite.commons import VarGetter
import awkward1 as ak
from pathlib import Path
import uproot4
import uproot as upwrite
import json

from sklearn.model_selection import train_test_split

class MLHolder:
    """Wrapper for XGBoost training. Takes an uproot input, a list of
    groups to do a multiclass training, as well as a cut string if
    needed and trains the data. After it is done, the results can be
    outputed to be piped into MVAPlotter

    Args:
      split_ratio(float): Ratio of test events for train test splitting
      group_names(list): List of the names of the different groups
      pred_train(dict): Dictionary of group name to BDT associated with it for train set
      pred_test(dict): Dictionary of group name to BDT associated with it for test set
      train_set(pandas.DataFrame): DataFrame of the training events
      test_set(pandas.DataFrame): DataFrame of the testing events
      cuts(list): List of ROOT style cuts to apply
      param(dict): Variables used in the training

    """
    def __init__(self, use_vars, groupDict):
        """Constructor method
        """
        self.group_names = list(groupDict.keys())
        self.group_dict = groupDict
        self.pred_train = dict()
        self.pred_test = dict()
        self.sample_map = dict()
        
        self.use_vars = use_vars
        self._include_vars = list(use_vars.keys())
        self._drop_vars = ["classID", "groupName", "finalWeight", "scale_factor"]
        self._all_vars = self._include_vars + self._drop_vars
        self.train_set = pd.DataFrame(columns=self._all_vars)
        self.test_set = pd.DataFrame(columns=self._all_vars)

        for key, func in self.use_vars.items():
            dtype = "int" if "num" in func else 'float'
            self.train_set[key] = self.train_set[key].astype(dtype)
            self.test_set[key] = self.test_set[key].astype(dtype)

        self.param = dict()

    # def get_final_dict(self, directory):
    #     arr_dict = dict()
    #     path = Path(directory)
    #   root_files = path.rglob("*.root") if path.is_dir() else [path]
    #     for root_file in root_files:
    #         groups = list()
    #         with uproot4.open(root_file) as f:
    #             groups = [key.strip(";1") for key in f.keys() if "/" not in key]
    #         for group in groups:
    #             if group not in arr_dict:
    #                 arr_dict[group] = VarGetter(root_file, group)
    #             else:
    #                 arr_dict[group] += VarGetter(root_file, group)

    #     return arr_dict

    # def setup_test_train(self, arr, group, sample, class_id, noTrain):
    #     sumW = ak.sum(arr.scale)
    #     totalEv = len(arr.scale)

    #     df_dict = dict()
    #     for varname, func in self.use_vars.items():
    #         df_dict[varname] = ak.to_numpy(eval("arr.{}".format(func)))
    #     df_dict["scale_factor"] = ak.to_numpy(arr.scale)

    #     df = pd.DataFrame.from_dict(df_dict)
    #     df = self._cut_frame(df)
    #     df["classID"] = class_id
    #     df["groupName"] = sample
    #     genWeightFactor = sumW/np.sum(abs(df.scale_factor))
    #     df["finalWeight"] = abs(df.scale_factor)*genWeightFactor
    #     total_evts = len(df)
    #     if noTrain:
    #         self.test_set = pd.concat([df.reset_index(drop=True), self.test_set], sort=True)
    #         print("Add Tree {} of type {}".format(sample, group))
    #         return 0, 0
    #     split_ratio = self.split_ratio if len(df) < self.max_events else self.max_events
    #     train, test = train_test_split(df, train_size=split_ratio,
    #                                random_state=12345)
    #     self.test_set = pd.concat([test.reset_index(drop=True), self.test_set], sort=True)
    #     self.train_set = pd.concat([train.reset_index(drop=True), self.train_set], sort=True)
    #     print("Add Tree {} of type {} with {} rawevents and {:.2E} events"
    #           .format(sample, group, len(train), np.sum(df.scale_factor)))
    #     return sumW, totalEv

    def setup_files(self, directory, year="2018"):
        """**Fill the dataframes with all info in the input files**

        This grabs all the variable information about each sample,
        does some preliminary weighting and splits the data into the
        test and train set (based on `self.split_ratio`)

        Args:
            directory(string): Path to directory where root files are kept
        """
        train_file = "{}/train.root".format(directory)
        test_file = "{}/{}/train.root".format(directory, year)
        classID = {"Signal": 1, "NotTrained": -1, "Background": 0}


        with uproot4.open(train_file) as f:
            groups = json.loads(f["sample_map"]).keys()
            for group in groups:
                self.train_set = pd.concat([f[group].arrays(library="pd"), self.train_set], sort=True)
        with uproot4.open(test_file) as f:
            self.sample_map = json.loads(f["sample_map"])
            groups = json.loads(f["sample_map"]).keys()
            for group in groups:
                self.test_set = pd.concat([f[group].arrays(library="pd"), self.train_set], sort=True)

        self.train_set["finalWeight"] = 1.
        for group, samples in self.group_dict.items():
            clsID =  classID[group]
            if group == "NotTrained":
                continue
            group_set = self.train_set[self.train_set["classID"] == clsID]
            scale = 1.*len(group_set)/sum(group_set["scale_factor"])
            print(np.unique(group_set["groupName"]))
            for sample in samples:
                sampleID = self.sample_map[sample]
                sampleScale = group_set[group_set["groupName"] == sampleID]["scale_factor"]
                sumW = sum(sampleScale)
                finalWeight = scale*abs(sampleScale)*sumW/np.sum(abs(sampleScale))
                self.train_set[self.train_set["groupName"] == sampleID]["finalWeight"] = finalWeight

    def train(self):
        pass

    def apply_model(self, model_file):
        pass

    def output(self, outdir):
        """Wrapper for write out commands

        Args:
          outname: Directory where files will be written

        """
        self._write_uproot("{}/test.root".format(outdir), self.test_set,
                           self.pred_test)
        self._write_uproot("{}/train.root".format(outdir), self.train_set,
                           self.pred_train)

    # Private Functions

    def _cut_frame(self, frame):
        """**Reduce frame using root style cut string**

        Args:
          frame(pandas.DataFrame): DataFrame to cut on

        """
        for cut in self.cuts:
            if cut.find("<") != -1:
                tmp = cut.split("<")
                frame = frame[frame[tmp[0]] < float(tmp[1])]
            elif cut.find(">") != -1:
                tmp = cut.split(">")
                frame = frame[frame[tmp[0]] > float(tmp[1])]
            elif cut.find("==") != -1:
                tmp = cut.split("==")
                frame = frame[frame[tmp[0]] == float(tmp[1])]
        return frame

    def add_cut(self, cut_string):
        self.cuts = cut_string

    def _write_uproot(self, outfile, workSet, prediction=dict()):
        """**Write out pandas file as a compressed pickle file

        Args:
          outfile(string): Name of file to write
          workSet(pandas.DataFrame): DataFrame of variables to write out
          prediction(pandas.DataFrame): DataFrame of BDT predictions

        """
        for key, arr in prediction.items():
            workSet.insert(0, key, arr)

        keepList = [key for key in workSet.columns if is_numeric_dtype(workSet[key])]
        branches = {key: workSet[key].dtype for key in keepList}
        with upwrite.recreate(outfile) as f:
            for group in np.unique(workSet.groupName):
                groupSet = workSet[workSet.groupName == group][keepList]
                f[group] = upwrite.newtree(branches)
                f[group].extend(groupSet.to_dict('list'))

        # workSet.to_parquet(outname, compression="gzip")
