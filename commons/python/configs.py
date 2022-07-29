#!/usr/bin/env python3
import argparse
import sys
import pkgutil
import time
import numpy as np
import uproot
from contextlib import contextmanager

def get_cli():
    from .user import workspace_area
    import analysis_suite.data.plotInfo as plotInfo

    parser = argparse.ArgumentParser(prog="main", description="Central script for running tools in the Analysis suite")
    parser.add_argument('tool', type=str, help="Tool to run",
                    choices=['mva', 'plot', 'analyze', 'combine'])
    ##################
    # Common options #
    ##################
    parser.add_argument("-d", "--workdir", required=True, type=lambda x : workspace_area / x,
                        help="Working Directory")
    parser.add_argument("-j", type=int, default=1, help="Number of cores")
    parser.add_argument("--log", type=str, default="ERROR",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help="Set debug status (currently not used)")
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")
    parser.add_argument("-s", "--systs", default="Nominal",
                        type=lambda x : [i.strip() for i in x.split(',')],
                        help="Systematics to be used")
    histInfo = [ f.name for f in pkgutil.iter_modules(plotInfo.__path__) if not f.ispkg]
    parser.add_argument("-i", "--info", type=str, default="plotInfo_default",
                        choices=histInfo,
                            help="Name of file containing histogram Info")
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1] == "mva":
        parser.add_argument('-t', '--train', default="None",
                            choices=['None', 'DNN', 'TMVA', 'XGB', "CutBased"],
                            help="Run the training")
        parser.add_argument("-m", '--apply_model', action='store_true')
        parser.add_argument("--save", action='store_true')
        parser.add_argument("--plot", action='store_true')
        parser.add_argument('-r', '--regions', default="Signal",
                            type=lambda x : [i.strip() for i in x.split(',')],)
    elif sys.argv[1] == "plot":
        parser.add_argument("--hists", default="all",
                            type=lambda x : ["all"] if x == "all" \
                            else [i.strip() for i in x.split(',')],
                            help="Pick specific histogram to plot")
        parser.add_argument("--drawStyle", type=str, default='stack',
                            help='Way to draw graph',
                            choices=['stack', 'compare', 'sigratio'])
        parser.add_argument("--stack_signal", action='store_true',
                            help="Stack signal hists on top of background")
        parser.add_argument("--ratio_range", nargs=2, default=[0.4, 1.6],
                            help="Ratio min ratio max (default 0.5 1.5)")
        parser.add_argument('-t', '--type', default='processed', choices=['processed', 'test', 'train'],
                            help='Type of file in the analysis change')
        parser.add_argument('-r', '--region', default='Signal',
                            help='Region that this histogram will be plotted from')
    else:
        pass

    # Combos
    if len(sys.argv) > 1 and (sys.argv[1] == "plot" or sys.argv[1] == "combine"):
        parser.add_argument("-sig", "--signal", type=str, default='', required=True,
                            help="Name of the group to be made into the Signal")

    return parser.parse_args()


def findScale(ratio):
    sigNum = 10**int(np.log10(ratio))
    tot = int((ratio) / sigNum) * sigNum
    if ratio > tot + sigNum//2:
        tot += sigNum//2
    return tot

def checkOrCreateDir(path):
    if not path.is_dir():
        path.mkdir(parents=True)


def getGroupDict(groups, group_info):
    groupDict = {}
    allSamples = set()
    for groupName, samples in groups.items():
        new_samples = list()
        for samp in samples:
            if samp in group_info.group2MemberMap:
                new_samples += group_info.group2MemberMap[samp]
            else:
                new_samples.append(samp)
        if allSamples.intersection(new_samples):
            raise Exception("Group has overlap, probably from same sample groups repeated. Change this")
        allSamples = allSamples.union(new_samples)
        groupDict[groupName] = new_samples
    return groupDict


def get_list_systs(infile, tool, systs=["all"], **kwargs):
    allSysts = set()
    if tool == 'analyze':
        if infile.is_dir():
            all_files = list(infile.glob('*root'))
        else:
            all_files = [infile]
        for file_ in all_files:
            with uproot.open(file_) as f:
                for key in f.keys() :
                    if "Systematics" not in key:
                        continue
                    allSysts |= set(get_systs(f[key]))
    elif tool == 'mva':
        for f in infile.glob("**/processed*root"):
            allSysts |= {"_".join(f.stem.split('_')[1:-1])}

    return allSysts

def clean_syst(syst):
    return syst.replace("_down","").replace("_up","")

def get_plot_area(analysis, drawStyle, path):
    from .user import www_area
    extraPath = time.strftime("%Y_%m_%d")
    if path:
        extraPath = path / extraPath
    return www_area /'PlottingResults' / analysis / f'{extraPath}_{drawStyle}'

def make_plot_paths(path):
    checkOrCreateDir(path / "plots")
    checkOrCreateDir(path / "logs")

def get_shape_systs(addVar=False):
    from analysis_suite.data.inputs import systematics
    systs = [syst.name for syst in systematics if syst.syst_type == "shape"]
    if addVar:
        systs = [syst+"_up" for syst in systs] + [syst+"_down" for syst in systs ]
    return systs

def get_metadata(tlist, varName):
    for item in tlist:
        if item.member('fName') == varName:
            return item.member('fTitle')
    return None

def get_systs(tlist):
    return np.unique([item.member('fName') for item in tlist])

def get_syst_index(filename, systName):
    with uproot.open(filename) as f:
        syst_dir = [key for key in f.keys() if "Systematics" in key][0]
        systNames = [name.member("fName") for name in f[syst_dir]]
    if systName not in systNames:
        return -1
    else:
        return systNames.index(systName)

def get_dirnames(filename):
    with uproot.open(filename) as f:
        dirnames = [d for d, cls in f.classnames().items() if cls == "TDirectory"]
        if not dirnames:
            return None
        return {d.partition(";")[0] for d in dirnames}



@contextmanager
def rOpen(filename, option=""):
    import ROOT
    rootfile = ROOT.TFile(filename, option)
    yield rootfile
    rootfile.Close()

@np.vectorize
def asymptotic_sig(s, b):
    return s/np.sqrt(b+1e-5)

@np.vectorize
def likelihood_sig(s, b):
    return np.sqrt(2*(s+b)*np.log(1+s/(b+1e-5))-2*s)
