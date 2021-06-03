#!/usr/bin/env python3
import os
from analysis_suite.commons import FileInfo
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")


def setInputs(inputs):
    root_inputs = ROOT.TList()
    for key, value in inputs.items():
        item = None
        if isinstance(value, list):
            item = ROOT.TList()
            item.SetName(key)
            for subitem in value:
                item.Add(ROOT.TNamed(subitem, subitem))
        else:
            item = ROOT.TNamed(key, str(value))
        root_inputs.Add(item)
    return root_inputs


def getSumW(infiles):
    runChain = ROOT.TChain()
    sumweight = ROOT.TH1F("sumweight", "sumweight", 1, 0, 1)
    for fname in infiles:
        runChain.Add(f"{fname}/Runs")
    runChain.Draw("0>>sumweight",  "genEventSumw")
    return sumweight


if __name__ == "__main__":
    inputfile = "blah.in" if (env := os.getenv("INPUT")) is None else env
    outputfile = "output.root" if (env := os.getenv("OUTPUT")) is None else env

    files = list()
    with open(inputfile) as f:
        for line in f:
            files.append(line.strip())

    print(files)
    sampleName = files[0].split('/')
    analysisName = sampleName[sampleName.index("user")+2]

    analysis, year, selection = analysisName.split("_")
    info = FileInfo(analysis=analysis, year=year, selection=selection)

    # Setup inputs
    inputs = dict()
    groupName = info.get_group(sampleName)
    inputs["DAS_Name"] = sampleName
    inputs["Group"] = groupName
    inputs['Analysis'] = analysis
    inputs['Selection'] = selection
    inputs["Xsec"] = info.get_xsec(groupName)
    inputs["Year"] = year
    inputs["Systematics"] = ["LHEReweight"]
    inputs["isData"] = False
    rInputs = setInputs(inputs)

    # Run Selection
    fChain = ROOT.TChain()
    for fname in files:
        fChain.Add(f"{fname}/Events")

    selector = getattr(ROOT, "ThreeTop")()
    selector.SetInputList(rInputs)
    fChain.Process(selector, "")
    sumweight = getSumW(files)

    ## Output
    rOutput = ROOT.TFile(outputfile, "RECREATE")
    anaFolder = rOutput.mkdir(groupName)

    anaFolder.WriteObject(sumweight, "sumweight")
    for i in selector.GetOutputList():
        anaFolder.WriteObject(i, i.GetName())

    rOutput.Close()
