#!/usr/bin/env python3
import importlib
import numpy as np

class BasicInfo:
    def __init__(self, analysis="", selection="", **kwargs):
        self.analysis = analysis
        self.selection = selection
        self.base_path = "analysis_suite.data"

class PlotInfo(BasicInfo):
    lumi = {
        "2016" : 35.9,
        "2017" : 41.5,
        "2018" : 59.6,
        "all" : 137.0,
    }
    def __init__(self, plotInfo, **kwargs):
        super().__init__(**kwargs)
        plot_path = f'{self.base_path}.plotInfo.{plotInfo}'
        self.plotSpecs = importlib.import_module(plot_path).info

    def at(self, histname, name=None):
        if name is None:
            return self.plotSpecs[histname]
        elif name in self.plotSpecs[histname]:
            return self.plotSpecs[histname][name]
        else:
            return None

    def __getitem__(self, key):
        return self.plotSpecs[key]

    def get_hists(self, sublist):
        if sublist == ["all"]:
            return self.plotSpecs.keys()
        else:
            return list(set(self.plotSpecs.keys()) & set(sublist))

    def get_binning(self, histname):
        import boost_histogram as bh
        bins = np.array(self.at(histname, "Binning"), dtype=float)
        if self.at(histname, "Discrete"):
            bins[1:] = bins[1:] - 0.5
        return bh.axis.Regular(int(bins[0]), *bins[1:])

    def get_lumi(self, year):
        return self.lumi[year]

    def get_label(self, histname):
        return self.at(histname, "Label")

    def get_legend_loc(self, histname):
        loc = self.at(histname, "LegendLoc")
        return loc if loc is not None else "best"

class GroupInfo(BasicInfo):
    def __init__(self, group2color=None, **kwargs):
        super().__init__(**kwargs)
        group_path = f'{self.base_path}.PlotGroups.{self.analysis}'
        self.groupInfo = importlib.import_module(group_path).info
        self.group2color = group2color if group2color is not None else {}
        self.group2MemberMap = self.get_memberMap()

    def get_legend_name(self, group):
        return self.groupInfo[group]["Name"]

    def get_color(self, group):
        return self.group2color[group]

    def get_memberMap(self):
        keys = self.groupInfo.keys() if not self.group2color else self.group2color
        final = dict()
        for key in keys:
            if key not in self.groupInfo:
                continue
            info = self.groupInfo[key]
            members = info["Members"]
            if "Composite" in info and info["Composite"]:
                tmpMembers = list()
                for mem in members:
                    if mem in self.groupInfo:
                        tmpMembers += self.groupInfo[mem]["Members"]
                    else:
                        tmpMembers.append(mem)
                members = tmpMembers
            final[key] = members
        return final

class FileInfo(BasicInfo):
    def __init__(self, year="2018", **kwargs):
        super().__init__(**kwargs)
        self.year = int(year)
        file_path = f'{self.base_path}.FileInfo.{self.analysis}'
        self.fileInfo = importlib.import_module(file_path).info
        self.dasNames = {info["DAS"][self.year]: key for key, info in self.fileInfo.items()}

    def get_group(self, splitname):
        if self.is_data():
            return "data"
        elif isinstance(splitname, str) and splitname in self.dasNames:
            return self.dasNames[splitname]
        for name in splitname:
            if name in self.dasNames:
                return self.dasNames[name]
        return None

    def get_info(self, alias):
        return self.fileInfo[alias]

    def get_xsec(self, group):
        if self.is_data():
            return 1.
        info = self.get_info(group)
        scale = info['cross_section']
        if "kfactor" in info:
            scale *= info["kfactor"]
        return scale

    def is_data(self):
        return "data" in self.selection.lower()
