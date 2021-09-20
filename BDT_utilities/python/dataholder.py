#!/usr/bin/env python3

"""
.. module:: XGBoostMaker
   :synopsis: Takes in ROOT file to run a BDT training over it using XGBoost
.. moduleauthor:: Dylan Teague
"""
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from pandas.api.types import is_numeric_dtype
from pathlib import Path
from random import randint
import sys
import uproot4
import uproot as upwrite
import json
from analysis_suite.commons.configs import setup_pandas
from analysis_suite.commons.info import PlotInfo

from sklearn.metrics import roc_auc_score, confusion_matrix
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
        self.classID_by_className = {"Signal": 1, "Background": 0, "NotTrained": 0}
        self.group_dict = groupDict
        self.sample_map = dict()
        self.systName = systName

        self.use_vars = use_vars
        nonTrain_vars = ["scale_factor"]
        derived_vars = ["classID", "sampleName", "train_weight"]
        self._file_vars = list(use_vars.keys()) + nonTrain_vars
        self._drop_vars = nonTrain_vars + derived_vars
        self.all_vars = self._file_vars + derived_vars

        self.split_ratio = 0.3
        self.validation_ratio = 0.10
        self.max_train_events = 1000000
        self.min_train_events = 100
        self.random_state = randint(0, 2**32-1)#12345

        self.train_set = setup_pandas(self.use_vars, self.all_vars)
        self.validation_set = setup_pandas(self.use_vars, self.all_vars)
        self.test_sets = dict()

        self.pred_test = dict()
        self.auc = dict()
        self.fom = dict()


    def setup_year(self, directory, year="2018", save_train=False):
        """**Fill the dataframes with all info in the input files**

        This grabs all the variable information about each sample,
        does some preliminary weighting and splits the data into the
        test and train set (based on `self.split_ratio`)

        Args:
            directory(string): Path to directory where root files are kept
        """
        train_set= setup_pandas(self.use_vars, self.all_vars)
        test_set= setup_pandas(self.use_vars, self.all_vars)
        validation_set= setup_pandas(self.use_vars, self.all_vars)

        with uproot4.open(directory / year / f'processed_{self.systName}.root') as f:
            allSet = set([name[:name.index(";")] for name in f.keys()])
            self.update_sample_map(allSet)

            for className, samples in self.group_dict.items():
                for sample in samples:
                    if sample not in f:
                        print(f"{sample} not found")
                        continue
                    df = f[sample].arrays(self._file_vars, library="pd")
                    df.loc[:, "classID"] = self.classID_by_className[className]
                    df.loc[:, "sampleName"] = self.sample_map[sample]
                    df.loc[:, "train_weight"] = sum(df.scale_factor) / len(df)

                    split_ratio = self.split_ratio
                    if len(df) < self.min_train_events/split_ratio or className == "NotTrained":
                        test_set = pd.concat([df, test_set], ignore_index=True)
                        continue
                    elif len(df) > self.max_train_events/split_ratio:
                        split_ratio = self.max_train_events

                    test, train = self.split(df, split_ratio)
                    train, validation = self.split(train, self.validation_ratio)

                    train_set = pd.concat([train, train_set], ignore_index=True)
                    test_set = pd.concat([test, test_set], ignore_index=True)
                    validation_set = pd.concat([validation, validation_set], ignore_index=True)


        if save_train:
            self._output(train_set, directory / year / f"train_{self.systName}.root")
            self._output(validation_set, directory / year / f"validation_{self.systName}.root")

        self.train_set = pd.concat([self.class_reweight(train_set),
                                    self.train_set,], ignore_index=True)
        self.validation_set = pd.concat([validation, self.validation_set],
                                        ignore_index=True)
        self.test_sets[year] = test_set


    def split(self, workset, split_ratio):
        train, test = train_test_split(workset, train_size=split_ratio, random_state=self.random_state)
        test.loc[:, ["scale_factor", "train_weight"]] *= len(workset)/len(test)
        train.loc[:, ["scale_factor", "train_weight"]] *= len(workset)/len(train)
        return test, train


    def update_sample_map(self, allSet):
        for sample in (allSet - set(self.sample_map)):
            self.sample_map[sample] = len(self.sample_map)

    def class_reweight(self, workset):
        for className, classID in self.classID_by_className.items():
            class_mask = workset["classID"] == classID
            class_set = workset[class_mask]
            scale = len(class_set)/sum(class_set.train_weight)
            workset.loc[class_mask, "train_weight"] *= scale
        return workset


    def apply_model(self, directory, year):
        use_set = self.test_sets[year]
        pred = self.predict(use_set, directory)
        weights = use_set.scale_factor*137000.
        labels = use_set.classID.astype(int)

        self.pred_test[year] = {grp: pred.T[i] for grp, i in self.classID_by_className.items()}
        self.auc[year] = roc_auc_score(labels, pred.T[1],
                                       sample_weight = abs(weights)
                                       )

        self.fom[year] = 0
        fom_bins = np.linspace(0, 1, 101)
        sig = np.cumsum(np.histogram(self.pred_test[year]["Signal"][labels==1], bins=fom_bins,
                                     weights=weights[labels==1])[0][::-1])[::-1]
        tot = np.cumsum(np.histogram(self.pred_test[year]["Signal"], bins=fom_bins,
                                     weights=weights)[0][::-1])[::-1]
        self.fom[year] = max(sig/np.sqrt(tot))


        print(f'AUC for year {year}: {self.auc[year]}')
        print(f'FOM for year {year}: {self.fom[year]}')


    def get_stats(self, year, cut):
        truth_vals = self.test_sets[year].classID.astype(int)
        pred_mask = self.pred_test[year]["Signal"] > cut
        tn, fp, fn, tp = confusion_matrix(truth_vals, pred_mask).ravel()
        precision = tp / (tp+fp)
        recall = tp / (tp + fn)
        f1_score = 2*(precision*recall)/(precision+recall)
        s = (tp+fn)/len(truth_vals)
        p = (tp+fp)/len(truth_vals)

        cut_set = self.test_sets[year][pred_mask]

        sig = np.sum(cut_set[cut_set.classID == 1].scale_factor)
        bkg = np.sum(cut_set[cut_set.classID == 0].scale_factor)
        fom = sig/np.sqrt(sig+bkg)*np.sqrt(137*1000)

        matthew_coef = (tp/len(truth_vals)-s*p)/np.sqrt(p*s*(1-p)*(1-s))
        print(f'Cut {cut:0.3f} for year {year}: {precision:0.3f} {recall:0.3f} {f1_score:0.3f} {matthew_coef:0.3f} {fom:0.3f}')

    def _get_stats(self, year, cut, directory):
        work_set
        truth_vals = work_set.classID.astype(int)
        pred = self.predict(work_set, directory).T[1]
        tn, fp, fn, tp = confusion_matrix(truth_vals, pred >cut).ravel()
        precision = tp / (tp+fp)
        recall = tp / (tp + fn)
        f1_score = 2*(precision*recall)/(precision+recall)
        s = (tp+fn)/len(truth_vals)
        p = (tp+fp)/len(truth_vals)

        matthew_coef = (tp/len(truth_vals)-s*p)/np.sqrt(p*s*(1-p)*(1-s))
        print(f'Cut {cut:0.3f} for year {year}: {precision:0.3f} {recall:0.3f} {f1_score:0.3f} {matthew_coef:0.3f}')

    def predict(self, use_set, directory):
        print("Shouldn't be here")
        raise Exception("Calling base function")


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


    def output(self, outdir, year):
        workSet = self.test_sets[year]
        for key, arr in self.pred_test[year].items():
            workSet.insert(0, key, arr)
            self._output(workSet, outdir / year / f"test_{self.systName}.root")


    def _output(self, workSet, outfile):
        """**Write out pandas file as a compressed pickle file

        Args:
          workSet(pandas.DataFrame): DataFrame of variables to write out
          outfile(string): Name of file to write
        """
        keepList = [key for key in workSet.columns if is_numeric_dtype(workSet[key])]
        branches = {key: workSet[key].dtype for key in keepList}
        with upwrite.recreate(f'{outfile}.tmp') as f:
            for sample, value in self.sample_map.items():
                if value not in np.unique(workSet.sampleName):
                    continue
                f[sample] = upwrite.newtree(branches)
                f[sample].extend(workSet[workSet.sampleName == value][keepList].to_dict('list'))

        # rename to avoid losing file if root writing fails
        Path(f'{outfile}.tmp').rename(outfile)
