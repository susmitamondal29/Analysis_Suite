#!/usr/bin/env python3
import os
from analysis_suite.commons import FileInfo
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
        root_inputs.Add(subList)
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
    groupName = info.get_group(sampleName)

    # Setup inputs
    inputs = dict()
    inputs["MetaData"] = {
        "DAS_Name": ''.join(sampleName),
        "Group": groupName,
        'Analysis': analysis,
        'Selection': selection,
        'Xsec': info.get_xsec(groupName),
        'Year': year,
        'isData': False,
    }
    inputs["Systematics"] = ["LHE_muF", "LHE_muR", "BTagging"]
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
