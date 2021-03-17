#!/usr/bin/env python3
import numpy as np
import os
import glob
import imp
import subprocess
import importlib
from pathlib import Path

class BasicInfo:
    def __init__(self, analysis="", year="", selection="", lumi=140000, **kwargs):
        self.analysis = analysis
        self.selection = selection
        self.year = int(year)
        self.lumi = lumi
        self.base_path = "analysis_suite.data"

class PlotInfo(BasicInfo):
    def __init__(self, plotInfo, **kwargs):
        super().__init__(**kwargs)
        plot_path = "{}.plotInfo.{}".format(self.base_path, plotInfo)
        self.plotSpecs = importlib.import_module(plot_path).info

    def __getattr__(self, name):
        return {h: (vals[name] if name in vals else None) for h, vals in self.plotSpecs.items()}

    def __getitem__(self, key):
        return self.plotSpecs[key]

    def get_hists(self):
        return self.plotSpecs.keys()

    def get_binning(self, histname):
        import boost_histogram as bh
        bins = np.array(self.Binning[histname], dtype=float)
        if self.Discrete[histname]:
            bins[1:] = bins[1:] - 0.5
        return bh.axis.Regular(int(bins[0]), *bins[1:])

class GroupInfo(BasicInfo):
    def __init__(self, group2color={}, **kwargs):
        super().__init__(**kwargs)
        group_path = "{}.PlotGroups.{}".format(self.base_path, self.analysis)
        self.groupInfo = importlib.import_module(group_path).info
        self.group2color = group2color
        if group2color:
            self.group2MemberMap = {key: item["Members"] for key, item in
                                    self.groupInfo.items() if key in self.group2color}
        else:
            self.group2MemberMap = {key: item["Members"]
                                    for key, item in self.groupInfo.items()}

    def get_legend_name(self, group):
        return self.groupInfo[group]["Name"]

    def get_color(self, group):
        return self.group2color[group]

class FileInfo(BasicInfo):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        file_path = "{}.FileInfo.{}".format(self.base_path, self.analysis, self.year)
        self.fileInfo = importlib.import_module(file_path).info
        for key, info in self.fileInfo.items():
            self.fileInfo[key]["DAS"] = info["DAS"][self.year]

    def get_group(self, splitname):
        for key, info in self.fileInfo.items():
            if info["DAS"] in splitname:
                return key
        return None

    def get_info(self, alias):
        return self.fileInfo[alias]

    def get_xsec(self, group):
        info = self.get_info(group)
        scale = info['cross_section']
        if "kfactor" in info:
            scale *= info["kfactor"]
        return scale
