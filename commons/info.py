#!/usr/bin/env python3
import numpy as np
import os
import glob
import imp

class BasicInfo:
    def __init__(self, analysis="", selection="", lumi=140000, **kwargs):
        self.analysis = analysis
        self.selection = selection
        self.lumi = lumi

    def readAllInfo(self, file_path):
        info = {}
        for info_file in glob.glob(file_path):
            file_info = self.readInfo(info_file)
            if file_info:
                info.update(file_info)
        return info

    def readInfo(self, file_path):
        if ".py" not in file_path[-3:] and ".json" not in file_path[-5:]:
            if os.path.isfile(file_path + ".py"):
                file_path = file_path + ".py"
            elif os.path.isfile(file_path + ".json"):
                file_path = file_path + ".json"
            else:
                return
        if ".py" in file_path[-3:]:
            file_info = imp.load_source("info_file", file_path)
            info = file_info.info
        else:
            info = self.readJson(file_path)
        return info

    def readJson(self, json_file_name):
        json_info = {}
        with open(json_file_name) as json_file:
            try:
                json_info = json.load(json_file)
            except ValueError as err:
                print("Error reading JSON file {}. The error message was:"
                      .format(json_file_name))
                print(err)
        return json_info

class PlotInfo(BasicInfo):
    def __init__(self, plotInfo, **kwargs):
        super().__init__(**kwargs)
        self.plotSpecs = self.readAllInfo(plotInfo)

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


class FileInfo(BasicInfo):
    def __init__(self, group2color={}, **kwargs):
        super().__init__(**kwargs)
        self.group2color = group2color
        self.mcInfo = self.readAllInfo(
            "data/FileInfo/montecarlo/montecarlo_2016.py")
        self.fileInfo = self.readAllInfo(
            "data/FileInfo/{}/{}.py".format(self.analysis,self.selection))
        self.groupInfo = self.readAllInfo(
            "data/PlotGroups/{}.py".format(self.analysis))
        if group2color:
            self.group2MemberMap = {key: item["Members"] for key, item in
                                    self.groupInfo.items() if key in self.group2color}
        else:
            self.group2MemberMap = {key: item["Members"]
                                    for key, item in self.groupInfo.items()}


    def get_file_dict(self, group_list=None):
        if group_list is None:
            return {key: item["file_path"] for key, item in self.fileInfo.items()}
        else:
            return_dict = dict()
            for group in group_list:
                if group in self.group2MemberMap:
                    return_dict.update({sample: self.fileInfo[sample]["file_path"]
                                        for sample in self.group2MemberMap[group]})
                else:
                    return_dict[group] = self.fileInfo[group]["file_path"]
            return return_dict

    def get_xsec(self, group):
        scale = self.mcInfo[group]['cross_section']
        if "kfactor" in self.mcInfo[group]:
            scale *= self.mcInfo[group]["kfactor"]
        return scale

    def get_color(self, group):
        return self.group2color[group]

    def get_legend_name(self, group):
        return self.groupInfo[group]['Name']
