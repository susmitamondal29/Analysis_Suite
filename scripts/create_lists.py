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
            "DoubleMuon",
            "EGamma",
            "MuonEG",
        ],
    },

    "mc" : [
        # # TTT
        # 'TTTJ_TuneCP5*',
        # 'TTTW_TuneCP5*',

        # # TTTT
        # 'TTTT_TuneCP5*',

        # # TTX
        # 'TTWJetsToLNu_TuneCP5_13TeV*',
        # 'TTZToLLNuNu_M-10_TuneCP5_13TeV*',
        # 'TTZToLL_M-1to10_TuneCP5*',
        # 'ttHToNonbb_M125_TuneCP5*',
        # 'ttHTobb_M125_TuneCP5*'

        # # TTXY
        # 'TTHH_TuneCP5*',
        # 'TTWH_TuneCP5*',
        # 'TTWW_TuneCP5*',
        # 'TTWZ_TuneCP5*',
        # 'TTZH_TuneCP5*',
        # 'TTZZ_TuneCP5*',

        # # Xgamma
        # 'TGJets_TuneCP5*',
        # 'TTGamma_Dilept_TuneCP5_13TeV*',
        # 'TTGamma_Hadronic_TuneCP5*',
        # 'TTGamma_SingleLept_TuneCP5_13TeV*',
        # 'WGToLNuG_TuneCP5*',
        # 'WWG_TuneCP5*',
        # 'WZG_TuneCP5*',
        # 'ZGToLLG_01J_5f_TuneCP5*',

        # # VV Inclusive
        # 'WW_TuneCP5*',
        # 'WZ_TuneCP5*',
        # 'ZZ_TuneCP5*',

        # # VVV
        # 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
        # 'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
        # 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
        # 'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',

        # # Other
        # 'DYJetsToLL_M-10to50_TuneCP5*',
        # 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
        # 'GluGluHToZZTo4L_M125_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
        # 'ST_tW_Dilept_5f_DR_TuneCP5*',
        # 'TT_TuneCH3_13TeV-powheg-herwig7',
        # 'WJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
        # 'tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-amcatnlo-pythia8',

        # # DY HT binned
        # "DYJetsToLL_M-50_HT-*_TuneCP5*13TeV-madgraphMLM-pythia8",

        # # TTbar lepton binned
        # 'TTTo2L2Nu_TuneCP5_13TeV*',
        # 'TTToSemiLeptonic_TuneCP5_13TeV*',
        # 'TTToHadronic_TuneCP5_13TeV*',

        # # QCD
        # "QCD_Pt-20_MuEnrichedPt15_Tune*",
        # "QCD_Pt-*_MuEnrichedPt5_Tune*",
        # "QCD_Pt-*_EMEnriched_Tune*",
        # "QCD_Pt_*_bcToE_Tune*",

        # # VV
        # To be done
    ],
}



conditions = {
    "data" : {
        "2016" : [
            "Run2016B-ver2*UL2016_MiniAODv2_NanoAODv9-v*",
            "Run2016C*UL2016_MiniAODv2_NanoAODv9-v*",
            "Run2016D*UL2016_MiniAODv2_NanoAODv9-v*",
            "Run2016E*UL2016_MiniAODv2_NanoAODv9-v*",
            "Run2016F*UL2016_MiniAODv2_NanoAODv9-v*",
            "Run2016G*UL2016_MiniAODv2_NanoAODv9-v*",
            "Run2016H*UL2016_MiniAODv2_NanoAODv9-v*",
        ],
        "2017" : [
            "Run2017B-UL2017_MiniAODv2_NanoAODv9-v*",
            "Run2017C-UL2017_MiniAODv2_NanoAODv9-v*",
            "Run2017D-UL2017_MiniAODv2_NanoAODv9-v*",
            "Run2017E-UL2017_MiniAODv2_NanoAODv9-v*",
            "Run2017F-UL2017_MiniAODv2_NanoAODv9-v*",
        ],
        "2018": [
            "Run2018A-UL2018_MiniAODv2_NanoAODv9-v*",
            "Run2018B-UL2018_MiniAODv2_NanoAODv9-v*",
            "Run2018C-UL2018_MiniAODv2_NanoAODv9-v*",
            "Run2018D-UL2018_MiniAODv2_NanoAODv9-v*",
        ]
    },
    "mc" : {
        "2016pre":  ["RunIISummer20UL16NanoAODAPVv9*-106X_mcRun2_asymptotic_preVFP*v*"],
        "2016post": ["RunIISummer20UL16NanoAODv9*-106X_mcRun2_asymptotic_v*"],
        "2017":     ["RunIISummer20UL17NanoAODv9*-106X_mc2017_realistic_v*"],
        "2018":     ["RunIISummer20UL18NanoAODv9*-106X_upgrade2018_realistic_v*"],
    },

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
#             print(dataset)
#             # print(dataset, get_nevents(dataset))
#     print()
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
