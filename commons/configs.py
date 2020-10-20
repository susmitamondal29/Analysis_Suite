#!/usr/bin/env python3
import math
import argparse
import os


def get_generic_args(outdirReq=False, infilesReq=False, selectionReq=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outdir", type=str, required=outdirReq,
                        help="directory where to write masks")
    parser.add_argument("-a", "--analysis", type=str, required=True,
                        help="Specificy analysis used")
    parser.add_argument("-s", "--selection", type=str, required=False,
                        help="Specificy selection used")
    parser.add_argument("-c", "--channels", type=str, default="",
                        help="Channels to run over")
    parser.add_argument("-j", type=int, default=1, help="Number of cores")
    parser.add_argument("-f", "--filenames", required=infilesReq,
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default="", help="List of input file names, "
                        "as defined in AnalysisDatasetManager, separated "
                        "by commas")
    parser.add_argument("--info", type=str, default="plotInfo_default.py",
                        help="Name of file containing histogram Info")
    parser.add_argument("-l", "--lumi", type=float, default=140,
                        help="Luminsoity in fb-1. Default 35.9 fb-1. "
                        "Set to -1 for unit normalization")
    return parser

def pre(pre, lister):
    return ["_".join([pre, l]) for l in lister]

def findScale(ratio):
    sigNum = 10**int(math.log10(ratio))
    return int((ratio) / sigNum) * sigNum


def checkOrCreateDir(path):
    if not os.path.exists(path):
        os.makedirs(path)



def getNormedHistos(indir, info, histName, chan):
    groupHists = dict()
    ak_col = info.Column[histName]
    for group, members in info.group2MemberMap.items():
        groupHists[group] = Histogram(info.getLegendName(group),
                                      info.get_color(group),
                                      info.get_binning(histName))
        for mem in members:
            narray = ak.Array({})
            try:
                array = ak.from_parquet("{}/{}_cut.parquet".format(indir, mem),
                                        [ak_col, "scale_factor"])
            except:
                continue
            sf = array["scale_factor"]
            vals = array[ak_col]
            if info.Modify[histName]:
                vals = eval(info.Modify[histName].format("vals"))
                if len(vals) != len(sf):
                    sf,_ = ak.unzip(ak.cartesian([sf, array[ak_col]]))
                    sf = ak.flatten(sf)
            narray[ak_col] = vals
            narray["scale_factor"] = sf
            groupHists[group] += narray

    for name, hist in groupHists.items():
        if info.lumi < 0:
            scale = 1 / sum(hist.hist)
            hist.scale(scale)
        else:
            hist.scale(info.lumi)
    return groupHists

