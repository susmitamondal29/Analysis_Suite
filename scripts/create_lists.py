#!/usr/bin/env python3
import subprocess
import numpy as np
from pathlib import Path
import argparse
import itertools

xrd_tag = "root://cms-xrd-global.cern.ch/"
analysis = "ThreeTop"
runfile_dir = Path(__file__).parent / ".." / "runfiles"
if not runfile_dir.exists():
    runfile_dir.mkdir()


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True, help="output filename")
parser.add_argument("--local", help="Run for local files (skimmed files)")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_argument("--data", action="store_true", help="Run on data")
args = parser.parse_args()


selection = "NEWtopTagger-HT250-Bjet1-Leptons2"


datasets = {
    "data" : [
        "SingleMuon"
        # "DoubleMuon",
        # "MuonEG"
    ],
    "mc" : [
        # "QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        # "QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8",
        "WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        "TT_TuneCUETP8M2T4_13TeV-powheg-pythia8",
        "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
    ],
}



conditions = {
    "data" : [
        "Run2016B-02Apr2020_ver2*",
        "Run2016C-02Apr2020*",
        "Run2016D-02Apr2020*",
        "Run2016E-02Apr2020*",
        "Run2016F-02Apr2020*",
        "Run2016G-02Apr2020*",
        "Run2016H-02Apr2020*"
    ],

    "mc" : [
        "RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8*"
    ],
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
    return subprocess.check_output(query, shell=True).decode().split()

def local_list(year, selection):
    path = f'/store/user/dteague/{analysis}_{year}_{selection}'
    return subprocess.check_output(f"hdfs dfs -find {path} -name '*root'", shell=True).decode().split()



for year in args.years:
    with open(runfile_dir / f'{args.filename}_{year}.dat', "w") as f:
        if args.local:
            for root_files in local_list(year, selection):
                f.write(f'{root_files}\n')
        else:
            file_type = "data" if args.data else
            for cond, ds in itertools.product(conditions, datasets):
                for dataset in get_datasets(ds, cond, args.data):
                    print(dataset, len(get_files(dataset)))
                    for data_file in get_files(dataset):
                        f.write(f'{xrd_tag}{data_file}\n')
