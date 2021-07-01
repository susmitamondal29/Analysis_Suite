#!/usr/bin/env python3
import math
import argparse
import os
import sys
import shutil
import pkgutil
import time
from pathlib import Path
from collections import OrderedDict
import analysis_suite.data.PlotGroups as PlotGroups

def first_time_actions():
    inputs_file = Path("data/python/inputs.py")
    if not inputs_file.exists():
        shutil.copy("data/python/inputs_default.py", inputs_file)
        print("Please run \n\n  scram b\n\nto initialize inputs file")
        exit()



def get_cli():
    parser = argparse.ArgumentParser(prog="main", description="Central script for running tools in the Analysis suite")
    parser.add_argument('tool', type=str, help="Tool to run",
                    choices=['mva', 'plot', 'analyze', 'combine'])
    ##################
    # Common options #
    ##################
    parser.add_argument("-d", "--workdir", required=True,
                            help="Working Directory")
    analyses = [ f.name for f in pkgutil.iter_modules(PlotGroups.__path__) if not f.ispkg]
    parser.add_argument("-a", "--analysis", type=str, required=True,
                        choices=analyses, help="Specificy analysis used")
    parser.add_argument("-j", type=int, default=1, help="Number of cores")
    parser.add_argument("--log", type=str, default="WARNING",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help="Set debug status (currently not used)")
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")
    parser.add_argument("-s", "--systs", default="Nominal",
                        type=lambda x : [i.strip() for i in x.split(',')],
                        help="Systematics to be used")
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1] == "analyze":
        pass
    elif sys.argv[1] == "mva":
        parser.add_argument('-t', '--train', default="None",
                            choices=['None', 'DNN', 'TMVA', 'XGB'],
                            help="Run the training")
        parser.add_argument("-m", '--apply_model', action='store_true')
    elif sys.argv[1] == "plot":
        parser.add_argument("--hists", default="all",
                             type=lambda x : ["all"] if x == "all" \
                                        else [i.strip() for i in x.split(',')],
                             help="Pick specific histogram to plot")
        parser.add_argument("--drawStyle", type=str, default='stack',
                            help='Way to draw graph',
                            choices=['stack', 'compare', 'sigratio'])
        parser.add_argument("-sig", "--signal", type=str, default='',
                            help="Name of the group to be made into the Signal")
        parser.add_argument("--logy", action='store_true',
                            help="Use logaritmic scale on Y-axis")
        parser.add_argument("--stack_signal", action='store_true',
                            help="Stack signal hists on top of background")
        parser.add_argument("--ratio_range", nargs=2, default=[0.4, 1.6],
                            help="Ratio min ratio max (default 0.5 1.5)")
        parser.add_argument("--no_ratio", action="store_true",
                            help="Do not add ratio comparison")
        parser.add_argument("-i", "--info", type=str, default="plotInfo_default",
                        help="Name of file containing histogram Info")
    elif sys.argv[1] == "analyze":
        args, _ = parser.parse_known_args()
        selection = None
        if os.path.exists("data/FileInfo/"):
            selection = [f.name.strip(".py") for f in os.scandir(f'data/FileInfo/{args.analysis}')
                      if f.name.endswith("py") ] + ["CONDOR"]
        else:
             selection = ["CONDOR"]
        parser.add_argument("-s", "--selection", type=str, required=True,
                            choices = selection, help="Specificy selection used")
        parser.add_argument("-f", "--filenames", required=False,
                            type=lambda x : [i.strip() for i in x.split(',')],
                            default="", help="List of input file names, "
                            "as defined in AnalysisDatasetManager, separated "
                            "by commas")
        parser.add_argument("-r", "--rerun", type=str, help="Redo a function")

    elif sys.argv[1] == "combine":
        pass
    else:
        pass
    
    return parser.parse_args()


def pre(pre, lister):
    return ["_".join([pre, l]) for l in lister]

def findScale(ratio):
    sigNum = 10**int(math.log10(ratio))
    return int((ratio) / sigNum) * sigNum


def checkOrCreateDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def getNormedHistos(infilename, file_info, plot_info, histName, year):
    import awkward1 as ak
    import uproot4 as uproot
    from analysis_suite.commons.histogram import Histogram

    groupHists = dict()
    ak_col = plot_info.at(histName, "Column")
    for group, members in file_info.group2MemberMap.items():
        groupHists[group] = Histogram(file_info.get_legend_name(group),
                                      file_info.get_color(group),
                                      plot_info.get_binning(histName))
        with uproot.open(infilename) as f:
            for mem in members:
                if mem not in f:
                    print(f'problem with {mem} getting histogram {ak_col}')
                    continue
                array = f[mem].arrays([ak_col, "scale_factor"],)
                narray = {"name": mem}
                sf = array["scale_factor"]
                vals = array[ak_col]
                if plot_info.at(histName, "Modify"):
                    vals = eval(plot_info.at(histName, "Modify").format("vals"))
                    if len(vals) != len(sf):
                        sf,_ = ak.unzip(ak.cartesian([sf, array[ak_col]]))
                        sf = ak.flatten(sf)
                narray[ak_col] = vals
                narray["scale_factor"] = sf
                #print("{}: {:.3f}+-{:.3f} ({})".format(mem, ak.sum(sf)*plot_info.lumi, plot_info.lumi*math.sqrt(ak.sum(sf**2)),len(sf)))
                groupHists[group] += narray

    for name, hist in groupHists.items():
        # if plot_info.lumi < 0:
        #     scale = 1 / sum(hist.hist)
        #     hist.scale(scale)
        # else:
        hist.scale(plot_info.get_lumi(year)*1000)
    s, b = 0, 0
    for group, hist in groupHists.items():
        if group == "ttt":
            s = hist.integral()
        else:
            b += hist.integral()

    print("Figure of merit: ", s/math.sqrt(s+b+1e-9))
    return groupHists


def getGroupDict(groups, group_info):
    groupDict = OrderedDict()
    for groupName, samples in groups:
        new_samples = list()
        for samp in samples:
            if samp in group_info.group2MemberMap:
                new_samples += group_info.group2MemberMap[samp]
            else:
                new_samples.append(samp)
        groupDict[groupName] = new_samples
    return groupDict

def get_list_systs(filename, cli_systs=["all"]):
    allSysts = list()

    if filename.is_file():
        import numpy as np
        import uproot4 as uproot
        with uproot.open(filename) as f:
            for d in f:
                if "Systematics" not in d:
                    continue
                allSysts = np.unique([syst.member("fName") for syst in f[d]])
                break
    else:
        allSysts = [syst.name.replace("test_", "").replace(".root", "")
                    for syst in filename.glob("test*.root")]

    if cli_systs == ["all"]:
        return allSysts
    else:
        return [syst for syst in allSysts
                if syst.replace("_down","").replace("_up","") in cli_systs]

def get_plot_area(analysis, drawStyle, path):
    extraPath = time.strftime("%Y_%m_%d")
    if path:
        extraPath = path + '/' + extraPath

    if 'hep.wisc.edu' in os.environ['HOSTNAME']:
        basePath = Path(f'{os.environ["HOME"]}/public_html')
    elif 'uwlogin' in os.environ['HOSTNAME'] or 'lxplus' in os.environ['HOSTNAME']:
        basePath = Path('/eos/home-{0:1.1s}/{0}/www'.format(os.environ['USER']))
    basePath /= f'PlottingResults/{analysis}/{extraPath}_{drawStyle}'

    return basePath

def make_plot_paths(path):
    checkOrCreateDir(path)
    checkOrCreateDir(f'{path}/plots')
    checkOrCreateDir(f'{path}/logs')
