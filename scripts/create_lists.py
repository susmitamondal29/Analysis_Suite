#!/usr/bin/env python3
import subprocess
import numpy as np
from pathlib import Path
import argparse
import itertools
import re

from analysis_suite.commons.info import GroupInfo, FileInfo


xrd_tag = "root://cms-xrd-global.cern.ch/"
analysis = "ThreeTop"
runfile_dir = Path(__file__).parent / ".." / "runfiles"
if not runfile_dir.exists():
    runfile_dir.mkdir()


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True, help="output filename")
parser.add_argument("--local", action="store_true",
                    help="Run for local files (skimmed files)")
parser.add_argument('-g', "--groups",help="Groups to analyze",
                    type=lambda x : x.split(','))
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_argument('-t', "--type", help="Type of dataset to use")
args = parser.parse_args()


datasets = {
    "data" : {
        "2016": [
            "DoubleMuon",
            "DoubleEG",
            "MuonEG",
        ],
        "2017": [
            "DoubleMuon",
            "SingleElectron",
            "MuonEG",
        ],
        "2018": [
            # "DoubleMuon",
            "EGamma",
            # "MuonEG",
        ],
    },

    "mc" : [
        # "QCD_Pt-20toInf_MuEnrichedPt15_Tune*",
        # "QCD_Pt-15to20_MuEnrichedPt5_Tune*",
        # "QCD_Pt-20to30_MuEnrichedPt5_Tune*",
        # "QCD_Pt-30to50_MuEnrichedPt5_Tune*",
        # "QCD_Pt-50to80_MuEnrichedPt5_Tune*",
        # "QCD_Pt-80to120_MuEnrichedPt5_Tune*",
        # "QCD_Pt-120to170_MuEnrichedPt5_Tune*",
        # "QCD_Pt-170to300_MuEnrichedPt5_Tune*",
        # "QCD_Pt-300to470_MuEnrichedPt5_Tune*",
        # "QCD_Pt-470to600_MuEnrichedPt5_Tune*",
        # "QCD_Pt-600to800_MuEnrichedPt5_Tune*",
        # "QCD_Pt-800to1000_MuEnrichedPt5_Tune*",
        # "QCD_Pt-1000toInf_MuEnrichedPt5_Tune*",

        # "QCD_Pt-15to20_EMEnriched_Tune*",
        # "QCD_Pt-20to30_EMEnriched_Tune*",
        # "QCD_Pt-30to50_EMEnriched_Tune*",
        # "QCD_Pt-50to80_EMEnriched_Tune*",
        # "QCD_Pt-80to120_EMEnriched_Tune*",
        # "QCD_Pt-120to170_EMEnriched_Tune*",
        # "QCD_Pt-170to300_EMEnriched_Tune*",
        # "QCD_Pt-300toInf_EMEnriched_Tune*",

        # "QCD_Pt_15to20_bcToE_Tune*",
        # "QCD_Pt_20to30_bcToE_Tune*",
        # "QCD_Pt_30to80_bcToE_Tune*",
        # "QCD_Pt_80to170_bcToE_Tune*",
        # "QCD_Pt_170to250_bcToE_Tune*",
        # "QCD_Pt_250toInf_bcToE_Tune*",

        # "WJetsToLNu_Tune*madgraphMLM-pythia8",
        "TTJets_TuneCP5_13TeV-madgraphMLM-pythia8",
        "TTJets_DiLept_TuneCP5_13TeV-madgraphMLM-pythia8",
        # "TT_Tune*powheg*",
        # "DYJetsToLL_M-10to50_Tune*madgraphMLM-pythia8",
        "DYJetsToLL_M-50_TuneCP5*madgraphMLM-pythia8",

        # "DYJetsToLL_M-50_HT-40to70_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-70to100_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-100to200_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-200to400_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-400to600_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-600to800_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-800to1200_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-1200to2500_Tune*13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_HT-2500toInf_Tune*13TeV-madgraphMLM-pythia8",



    ],
}



conditions = {
    "data" : {
        "2016" : [
            "Run2016B-02Apr2020_ver2*",
            "Run2016C-02Apr2020*",
            "Run2016D-02Apr2020*",
            "Run2016E-02Apr2020*",
            "Run2016F-02Apr2020*",
            "Run2016G-02Apr2020*",
            "Run2016H-02Apr2020*"
        ],
        "2017" : [
            "Run2017B-02Apr2020*",
            "Run2017C-02Apr2020*",
            "Run2017D-02Apr2020*",
            "Run2017E-02Apr2020*",
            "Run2017F-02Apr2020*",
        ],
        "2018": [
            "Run2018A-02Apr2020*",
            "Run2018B-02Apr2020*",
            "Run2018C-02Apr2020*",
            "Run2018D-02Apr2020*",
        ]
    },
    "mc" : {
        "2016" : ["RunIISummer16NanoAOD*02Apr2020*_asymptotic_v*"],
        "2017" : ["RunIIFall17NanoAOD*02Apr2020*_realistic_v*"],
        "2018" : ["RunIIAutumn18NanoAOD*02Apr2020*_realistic_v*"],
    },
    "mcUL" : {
        "2016": ["RunIISummer20UL16MiniAOD*-106X_mcRun2_asymptotic_v*"],
        "2017": ["RunIISummer20UL17MiniAOD*-106X_mc2017_realistic_v*"],
        "2018": ["RunIISummer20UL18MiniAOD*-106X_upgrade2018_realistic_v*"],
    }
}

selection = {
    "mc": "NEWtopTagger-HT250-Bjet1-Leptons2",
    'data': 'DATA-HT250-Bjet1-Leptons2',
}

def get_nevents(dataset):
    query = f'dasgoclient -query="file dataset={dataset} | grep file.nevents"'
    file_sizes = subprocess.check_output(query, shell=True).decode().split()
    return sum(np.array(file_sizes, dtype=int))

def get_files(dataset):
    query = f'dasgoclient -query="file dataset={dataset}"'
    return subprocess.check_output(query, shell=True).decode().split()

def get_datasets(dataset, condition, isData):
    nano_type = "NANOAOD" if isData else "NANOAODSIM"
    query = f"dasgoclient -query='dataset=/{dataset}/{condition}/{nano_type}'"
    # print(query)
    return subprocess.check_output(query, shell=True).decode().split()

def local_list(year, selection, groups):
    path = f'/store/user/dteague/{analysis}_{year}_{selection}'
    files = subprocess.check_output(f"hdfs dfs -find {path} -name '*root'", shell=True).decode().split()

    if groups is not None:
        files_new = list()
        gInfo = GroupInfo({g:"" for g in groups})
        fInfo = FileInfo(year=year)
        for group, aliases in gInfo.get_memberMap().items():
            for alias in aliases:
                print(fInfo.dasNames[alias])
                group_list = list(filter(lambda x : re.match(".*/" + fInfo.dasNames[alias], x) is not None, files))
                files_new += group_list
        return files_new
    else:
        return files



# for year in args.years:
#     all_datasets = datasets[args.type] if isinstance(datasets[args.type], list) else datasets[args.type][year]
#     for cond, ds in itertools.product(conditions[args.type][year], all_datasets):
#         for dataset in get_datasets(ds, cond, "data" in args.type):
#             print(dataset, get_nevents(dataset))
# exit()

isData = "data" in args.type

for year in args.years:
    with open(runfile_dir / f'{args.filename}_{args.type}_{year}.dat', "w") as f:
        if args.local:
            for root_files in local_list(year, selection[args.type], args.groups):
                f.write(f'{root_files}\n')
        else:
            all_datasets = datasets[args.type] if isinstance(datasets[args.type], list) else datasets[args.type][year]
            for cond, ds in itertools.product(conditions[args.type][year], all_datasets):
                for dataset in get_datasets(ds, cond, isData):
                    print(dataset, len(get_files(dataset)), get_nevents(dataset))
                    for data_file in get_files(dataset):
                        f.write(f'{xrd_tag}{data_file}\n')
