#!/usr/bin/env python3
import ROOT
from scale_info import info
from analysis_suite.commons.configs import rOpen

def getInfo(info, name, year, keyName=""):
    if isinstance(info[name], dict):
        return {keyName: info[name][year]}
    elif isinstance(info[name], list):
        return {name: hist.format(year) for hist, name in info[name]}
    else:
        return {keyName: info[name].format(year)}


def write_scale(scale_name, scale_info, directory, year):
    infiles = getInfo(scale_info, "File", year)
    hists = getInfo(scale_info, "Histogram", year, scale_name)

    for wp, filename in infiles.items():
        with rOpen(filename) as f:
            for name, hist in hists.items():
                directory.WriteObject(getattr(f, hist).Clone(), name.format(wp))

years = [2016, 2017, 2018]

with rOpen("event_scalefactors.root", "RECREATE") as f:
    for year in years:
        workdir = f.mkdir(str(year))
        for scaleName, scaleInfo in info.items():
            write_scale(scaleName, scaleInfo, workdir, year)
