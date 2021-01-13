#!/usr/bin/env python3
import os

inputfile = os.getenv("INPUT")
outputfile = os.getenv("OUTPUT")

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")
def setInputs(inputs, list_THX=[]):
    root_inputs = ROOT.TList()
    for th1 in list_THX:
        root_inputs.Add(th1)
    for key, value in inputs.items():
        root_inputs.Add(ROOT.TParameter(type(value))(key, value))
    return root_inputs


inputs = {"a": 1, "b": True}
rInputs = setInputs(inputs)

files = list()
with open(inputfile) as f:
    for line in f:
        files.append(line)

fChain = ROOT.TChain()
for fname in files:
    fChain.Add(f"{fname}/Events")
selector = getattr(ROOT, "ThreeTop")()
selector.SetInputList(rInputs)
fChain.Process(selector, "")

## Output
rOutput = ROOT.TFile(outputfile, "RECREATE")
for i in selector.GetOutputList():
    rOutput.cd()
    i.Write()
    
runChain = ROOT.TChain()
sumweight = ROOT.TH1F("sumweight", "sumweight", 1, 0, 1)
for fname in files:
    runChain.Add(f"{fname}/Runs")
runChain.Draw("0>>sumweight",  "genEventSumw")
sumweight.Write()

rOutput.Close()
