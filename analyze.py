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

def run_jme(files, year, isMC):
    from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import createJMECorrector
    from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

    # (isMC=True, dataYear=2016, runPeriod="B", jesUncert="Total", redojec=False, jetType = "AK4PFchs", noGroom=False)
    jmeCorrections = createJMECorrector(isMC=isMC, dataYear=year, runPeriod="B",
                                        jesUncert="Total", jetType="AK4PFchs")

    # p=PostProcessor(".",fnames,"Jet_pt>150","",[jetmetUncertainties2016(),exampleModuleConstr()],provenance=True)
    p = PostProcessor(outputDir=".", inputFiles=files,
                      modules=[jmeCorrections()],)
    p.run()

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
    parser.add_argument("-v", "--verbose", default=0)
    args = parser.parse_args()
    inputfile = args.infile if (env := os.getenv("INPUT")) is None else env
    outputfile = args.outfile if (env := os.getenv("OUTPUT")) is None else env

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

    setup_jec(jecTagsMC[year])
    setup_jec(jerTagsMC[year])

    # Setup inputs
    inputs = dict()
    inputs["MetaData"] = {
        "DAS_Name": ''.join(sampleName),
        "Group": groupName,
        'Analysis': analysis,
        'Selection': selection,
        'Xsec': info.get_xsec(groupName),
        'Year': year,
        'isData': info.is_data(),
    }
    inputs["Verbosity"] = args.verbose
    inputs["Systematics"] = configs.get_shape_systs()
    rInputs = setInputs(inputs)

    # Run Selection
    fChain = ROOT.TChain()
    for fname in files:
        fChain.Add(f"{fname}/Events")

    selector = getattr(ROOT, "ThreeTop")()
    rOutput = ROOT.TFile(outputfile, "RECREATE")

    selector.SetInputList(rInputs)
    selector.setOutputFile(rOutput)
    fChain.Process(selector, "")
    sumweight = getSumW(files, info.is_data())

    ## Output
    for tree in selector.getTrees():
        anaFolder = getattr(rOutput, tree.tree.GetName())
        anaFolder.WriteObject(sumweight, "sumweight")
        tree.tree.SetName("Analyzed")
        tree.tree.SetTitle("Analyzed")
        anaFolder.WriteObject(tree.tree, "Analyzed")
        for i in selector.GetOutputList():
            anaFolder.WriteObject(i, i.GetName())

    rOutput.Close()
