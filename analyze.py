#!/usr/bin/env python3
import os
import argparse
from analysis_suite.commons import FileInfo
import analysis_suite.commons.configs as configs
import tarfile
from pathlib import Path

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")

jecTagsMC = {
    "2016": "Summer16_07Aug2017_V11_MC",
    "2017": "Fall17_17Nov2017_V32_MC",
    "2018": "Autumn18_V19_MC",
}
jerTagsMC = {
    "2016": "Summer16_25nsV1_MC",
    "2017": "Fall17_V3_MC",
    "2018": "Autumn18_V7b_MC",
}


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


def getSumW(infiles, isData):
    runChain = ROOT.TChain()
    sumweight = ROOT.TH1F("sumweight", "sumweight", 1, 0, 1)
    if isData:
        sumweight.SetBinContent(1, -1);
    else:
        for fname in infiles:
            runChain.Add(f"{fname}/Runs")
        runChain.Draw("0>>sumweight",  "genEventSumw")
    return sumweight

# Use for file in hdfs area
def get_info_local(filename):
    sampleName = filename.split('/')
    analysisName = sampleName[sampleName.index("user")+2]

    analysis, year, selection = analysisName.split("_")
    isUL = 'UL' in analysis
    return {"analysis": analysis, "year": year, "selection": selection,
            "sampleName": sampleName, "isUL": isUL}

def get_info_general(filename):
    sampleName = filename.split('/')
    analysis = "FakeRate"
    yearDict = {"Summer16": "2016",
                "Fall17": "2017",
                "Autumn18" : "2018",
                "UL16": "2016",
                "UL17": "2017",
                "UL18": "2018",
                "Run2016" : "2016",
                "Run2017" : "2017",
                "Run2018" : "2018",
                }
    year = None
    for yearName in yearDict.keys():
        if yearName in filename:
            year = yearDict[yearName]
            break

    isUL = "UL"  in filename
    return {"analysis": analysis, "year": year, "selection": "From_DAS",
            "sampleName": sampleName, "isUL": isUL}


def setup_jec(filename):
    jetType = "AK4PFchs"
    scaledir = Path(os.getenv("CMSSW_BASE"))/"src"/"analysis_suite"/"data"/"JEC"
    outdir = Path("jec_files")
    outdir.mkdir(exist_ok=True)

    with tarfile.open(scaledir / f"{filename}.tgz") as tar:
        for member in [name for name in tar.getnames() if jetType in name]:
            if (outdir/member).exists():
                continue
            tar.extract(member, path=outdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="main")
    parser.add_argument("-i", "--infile", default = "blah.in")
    parser.add_argument("-o", "--outfile", default="output.root")
    parser.add_argument("-v", "--verbose", default=-1)
    args = parser.parse_args()
    inputfile = args.infile if (env := os.getenv("INPUT")) is None else env
    outputfile = args.outfile if (env := os.getenv("OUTPUT")) is None else env

    files = list()
    with open(inputfile) as f:
        for line in f:
            files.append(line.strip())
    print(files)
    testfile = files[0]
    if "root://" in testfile:
                details = get_info_general(testfile)
    else:
        details = get_info_local(testfile)
    info = FileInfo(**details)
    groupName = info.get_group(details["sampleName"])

    setup_jec(jecTagsMC[details["year"]])
    setup_jec(jerTagsMC[details["year"]])

    # Setup inputs
    inputs = dict()
    inputs["MetaData"] = {
        "DAS_Name": '/'.join(details["sampleName"]),
        "Group": groupName,
        'Analysis': details["analysis"],
        'Selection': details["selection"],
        'Xsec': info.get_xsec(groupName),
        'Year': details["year"],
        'isData': info.is_data(groupName),
    }
    inputs["Verbosity"] = args.verbose
    inputs["Systematics"] = configs.get_shape_systs()
    # Possibly need to fix for fakefactor stuff
    rInputs = setInputs(inputs)

    # Run Selection
    fChain = ROOT.TChain()
    for fname in files:
        fChain.Add(f"{fname}/Events")

    selector = getattr(ROOT, details["analysis"])()


    with configs.rOpen(outputfile, "RECREATE") as rOutput:
        selector.SetInputList(rInputs)
        selector.setOutputFile(rOutput)
        fChain.Process(selector, "")

        ## Output
        anaFolder = selector.getOutdir()
        anaFolder.WriteObject(getSumW(files, info.is_data(groupName)), "sumweight")
        for tree in [tree.tree for tree in selector.getTrees()]:
            anaFolder.WriteObject(tree, tree.GetTitle())
        for i in selector.GetOutputList():
            anaFolder.WriteObject(i, i.GetName())
