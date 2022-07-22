#!/usr/bin/env python3
import os
import argparse
from analysis_suite.commons import FileInfo
import analysis_suite.commons.configs as configs
from pathlib import Path
import numpy as np
from multiprocessing import Pool
import subprocess
import yaml

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")

def setInputs(inputs):
    root_inputs = ROOT.TList()
    for key, data in inputs.items():
        subList = ROOT.TList()
        subList.SetName(key)
        if isinstance(data, dict):
            for dataName, dataVal in data.items():
                subList.Add(ROOT.TNamed(dataName, str(dataVal)))
        elif isinstance(data, list):
            for subitem in data:
                subList.Add(ROOT.TNamed(subitem, subitem))
        elif isinstance(data, (str, int, float, bool)):
            root_inputs.Add(ROOT.TNamed(key, str(data)))
            continue
        root_inputs.Add(subList)
    return root_inputs


def getSumW(infiles):
    runChain = ROOT.TChain()
    sumweight = ROOT.TH1F("sumweight", "sumweight", 1, 0, 1)
    for fname in infiles:
        runChain.Add(f"{fname}/Runs")

    if runChain.GetBranchStatus("genEventSumw"):
        runChain.Draw("0>>sumweight",  "genEventSumw")
    else:
        pass
    return sumweight

# Use for file in hdfs area
def get_info_local(filename):
    year="2016"
    return {"year": year, "sampleName": "data", "selection": "test"}

def get_info_general(filename):
    sampleName = filename.split('/')

    yearDict = {"UL16NanoAODAPVv": "2016preVFP",
                "UL16NanoAODv": "2016postVFP",
                "UL17": "2017",
                "UL18": "2018",
                "Run2016" : "2016postVFP",
                "Run2017" : "2017",
                "Run2018" : "2018",
                }
    year = None
    for yearName, yearkey in yearDict.items():
        if yearName in filename:
            if yearkey == "2016postVFP" and "HIPM" in filename:
                year = "2016preVFP"
            else:
                year = yearkey
            break

    isUL = "UL"  in filename
    return {"year": year, "selection": "From_DAS",
            "sampleName": sampleName}

def run_multi(start, evts, files, inputs, selector):
    fChain = ROOT.TChain()
    for fname in files:
        fChain.Add(f"{fname}/Events")

    selector = getattr(ROOT, inputs["MetaData"]["Analysis"])()
    rInputs = setInputs(inputs)

    with configs.rOpen(f"tmp_{start}.root", "RECREATE") as rOutput:
        selector.SetInputList(rInputs)
        selector.setOutputFile(rOutput)
        fChain.Process(selector, "", evts, start)

        anaFolder = selector.getOutdir()
        for tree in [tree.tree for tree in selector.getTrees()]:
            anaFolder.WriteObject(tree, tree.GetTitle())
        for i in selector.GetOutputList():
            anaFolder.WriteObject(i, i.GetName())
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="main")
    parser.add_argument("-i", "--infile", default = "blah.in")
    parser.add_argument("-o", "--outfile", default="output.root")
    parser.add_argument("--test", action='store_true')
    parser.add_argument("-v", "--verbose", default=-1)
    parser.add_argument("-a", "--analysis")
    parser.add_argument("-j", "--cores", default = 1, type=int)
    args = parser.parse_args()

    inputfile = args.infile if (env := os.getenv("INPUT")) is None else env
    outputfile = args.outfile if (env := os.getenv("OUTPUT")) is None else env

    if "root" == inputfile[inputfile.rindex(".")+1:]:
        files = [inputfile]
    else:
        with open(inputfile) as f:
            files = [line.strip() for line in f]

    testfile = files[0]
    if "root://" in testfile and "user" not in testfile:
        details = get_info_general(testfile)
    else:
        details = get_info_local(testfile)
    info = FileInfo(**details)
    groupName = info.get_group(details["sampleName"])
    datadir = Path(os.getenv("CMSSW_BASE"))/"src"/"analysis_suite"/"data"

    if args.analysis:
        analysis = args.analysis
    else:
        with open(datadir /".analyze_info") as f:
            analysis = f.readline().strip()

    # Setup inputs
    inputs = dict()
    inputs["MetaData"] = {
        "DAS_Name": '/'.join(details["sampleName"]),
        "Group": groupName,
        'Analysis': analysis,
        'Selection': details["selection"],
        'Year': details["year"],
    }
    if args.test:
        inputs['MetaData'].update({'Xsec': 1, 'isData': True})
    else:
        inputs['MetaData'].update({'Xsec': info.get_xsec(groupName), 'isData': info.is_data(groupName)})
    inputs["Verbosity"] = args.verbose
    inputs["Systematics"] = configs.get_shape_systs()
    # Possibly need to fix for fakefactor stuff
    rInputs = setInputs(inputs)
    if int(args.verbose) > 0:
        print(yaml.dump(inputs, indent=4, default_flow_style=False))

    # Run Selection
    fChain = ROOT.TChain()
    for fname in files:
        fChain.Add(f"{fname}/Events")

    nEntries= fChain.GetEntries()
    job_size = np.ceil(nEntries/args.cores)
    starts = np.arange(nEntries, step=job_size)
    steps = job_size*np.ones(args.cores)
    steps[-1] += nEntries - np.sum(steps)
    
    if args.cores == 1:
        selector = getattr(ROOT, analysis)()

        with configs.rOpen(outputfile, "RECREATE") as rOutput:
            selector.SetInputList(rInputs)
            selector.setOutputFile(rOutput)
            fChain.Process(selector, "")
            ## Output
            anaFolder = selector.getOutdir()
            anaFolder.WriteObject(getSumW(files), "sumweight")
            for tree in [tree.tree for tree in selector.getTrees()]:
                anaFolder.WriteObject(tree, tree.GetTitle())
            for i in selector.GetOutputList():
                anaFolder.WriteObject(i, i.GetName())
    else:
        argList = []
        for start, step in zip(starts, steps):
            argList.append((int(start), int(step), files, inputs, getattr(ROOT, inputs["MetaData"]["Analysis"])()))

        with Pool(args.cores) as pool:
            pool.starmap(run_multi, argList)

        subprocess.call(f"hadd -f -v 1 {outputfile} tmp*.root", shell=True)
        with configs.rOpen(outputfile, "UPDATE") as rOutput:
            anaFolder = rOutput.GetDirectory(groupName)
            anaFolder.WriteObject(getSumW(files), "sumweight")

        for tmp_file in Path(".").glob("tmp*root"):
            tmp_file.unlink()
