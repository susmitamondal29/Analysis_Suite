#!/usr/bin/env python3
import importlib
import numpy as np
import re

class BasicInfo:
    def __init__(self, selection="", **kwargs):
        self.selection = selection
        self.base_path = "analysis_suite.data"

class GroupInfo(BasicInfo):
    def __init__(self, group2color=None, **kwargs):
        super().__init__(**kwargs)
        group_path = f'{self.base_path}.PlotGroups'
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

    def get_members(self, group):
        return self.get_memberMap()[group]

    def setup_groups(self, groups=None):
        group_dict = dict()
        if groups is None:
            groups = self.group2color.keys()
        for group in groups:
            group_dict[group] = [mem for mem in self.get_members(group)]
        return group_dict


class FileInfo(BasicInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        file_name = "UL" # if isUL else "Legacy"
        file_path = f'{self.base_path}.FileInfo.{file_name}'
        self.fileInfo = importlib.import_module(file_path).info
        self.dasNames = {key: info["DAS"] for key, info in self.fileInfo.items()}

    def get_group(self, splitname):
        if isinstance(splitname, str) and splitname in self.dasNames:
            return self.dasNames[splitname]
        elif self.is_data(splitname):
            return 'data'

        sample_name = next(filter(lambda x: "13TeV" in x, splitname), None)
        for name, reName in self.dasNames.items():
            if re.match(reName, sample_name) is not None:
                return name
        return None

    def get_info(self, alias):
        return self.fileInfo[alias]

    def get_xsec(self, group):
        if self.is_data(group):
            return 1.
        info = self.get_info(group)
        scale = info['cross_section']
        if "kfactor" in info:
            scale *= info["kfactor"]
        return scale

    def is_data(self, group):
        if group == 'data':
            return True
        for split in map(str.lower, group):
            if "data" in split:
                return True
        return False

fileInfo = FileInfo()
