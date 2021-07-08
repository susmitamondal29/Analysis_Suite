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
import awkward1 as ak
from pathlib import Path
import uproot4
import uproot as upwrite
import json
from analysis_suite.commons.configs import setup_pandas

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
    def __init__(self, use_vars, groupDict, systName="Nominal", **kwargs):
        """Constructor method
        """
        self.group_names = list(groupDict.keys())
        self.group_dict = groupDict
        self.pred_train = dict()
        self.pred_test = dict()
        self.sample_map = dict()
        self.systName = systName

        self.use_vars = use_vars

        nonTrain_vars = ["classID", "groupName", "scale_factor"]
        derived_vars = ["finalWeight"]
        self._file_vars = list(use_vars.keys()) + nonTrain_vars
        self._drop_vars = nonTrain_vars + derived_vars

        all_vars = self._file_vars + derived_vars
        self.train_set, self.test_set = setup_pandas(self.use_vars, all_vars)

        self.param = dict()
        self.auc_train = 0.
        self.auc_test = 0.


    def setup_files(self, directory, year="2018", train=False):
        """**Fill the dataframes with all info in the input files**

        This grabs all the variable information about each sample,
        does some preliminary weighting and splits the data into the
        test and train set (based on `self.split_ratio`)

        Args:
            directory(string): Path to directory where root files are kept
        """
        if train:
            train_file = directory / f'train_{self.systName}.root'
            test_file = directory / f'train_{self.systName}.root'
        else:
            train_file = directory / year / f'train_{self.systName}.root'
            test_file = directory / year / f'test_{self.systName}.root'
        classID = {"Signal": 1, "NotTrained": -1, "Background": 0}

        with uproot4.open(test_file) as f:
            self.sample_map = json.loads(f["sample_map"])

        self.train_set = self.get_samples(train_file, self.train_set, train=True)
        self.test_set = self.get_samples(test_file, self.test_set)

        for group, samples in self.group_dict.items():
            clsID =  classID[group]
            if group == "NotTrained":
                continue
            group_set = self.train_set[self.train_set["classID"] == clsID]
            scale = 1.*len(group_set)/sum(group_set["scale_factor"]) if len(group_set) != 0 else 0
            for sample in samples:
                if sample not in self.sample_map:
                    continue
                sampleID = self.sample_map[sample]
                sampleScale = group_set[group_set["groupName"] == sampleID]["scale_factor"]
                sumW = sum(sampleScale)
                finalWeight = scale*abs(sampleScale)*sumW/np.sum(abs(sampleScale))
                self.train_set.loc[self.train_set["groupName"] == sampleID, "finalWeight"] = finalWeight

    def train(self):
        pass

    def apply_model(self, model_file):
        pass

    def get_samples(self, filename, inset, train=False):
        train_groups = sum(self.group_dict.values(), [])
        with uproot4.open(filename) as f:
            groups = [group for group in self.sample_map.keys()
                      if group in f and (not train or group in train_groups)]
            for group in groups:
                inset = pd.concat([f[group].arrays(self._file_vars, library="pd"), inset], sort=True)
        inset["finalWeight"] = 1.
        return inset

    def output(self, outdir, year, syst):
        """Wrapper for write out commands

        Args:
          outname: Directory where files will be written

        """
        self._write_uproot(outdir / year / f'test_{syst}.root', self.test_set,
                           self.pred_test)
        self._write_uproot(outdir / year / f'train_{syst}.root', self.train_set,
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
        with upwrite.recreate(f'{outfile}.tmp') as f:
            f["sample_map"] = json.dumps(self.sample_map)
            for group, value in self.sample_map.items():
                if value not in np.unique(workSet.groupName):
                    continue
                f[group] = upwrite.newtree(branches)
                f[group].extend(workSet[workSet.groupName == value][keepList].to_dict('list'))

        # rename to avoid losing file if root writing fails
        Path(f'{outfile}.tmp').rename(outfile)
