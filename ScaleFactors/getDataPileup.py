#!/usr/bin/env python3
import subprocess

goldenJson = {
    # https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2016Analysis
    2016: "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt",
    # https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2017Analysis
    2017: "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt",
    # https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2018Analysis
    2018: "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt",
}

pileup_latest = {
    # https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Location_of_central_pileup_files
    2016: "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt",
    2017: "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt",
    2018: "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt",
}
minbias = 69200
bins = 150
uncert = 0.046
systematics = {"nom": minbias,
               "up": minbias*(1+uncert),
               "dn": minbias*(1-uncert),
               }

command = ["pileupCalc.py",
           "--calcMode", "true",
           "--maxPileupBin", str(bins), "--numPileupBins", str(bins),]

yearCommands = list()

for year in [2016, 2017, 2018]:
    for syst, bias in systematics.items():
        yearCommands.append(["-i", goldenJson[year],
                              "--inputLumiJSON", pileup_latest[year],
                              "--minBiasXsec", str(bias),
                              f'data/dataPileup_{year}_{syst}.root'])


for yearCommand in yearCommands:
    print(" ".join(command+yearCommand))
    subprocess.run(command+yearCommand)
