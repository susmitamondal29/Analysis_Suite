#!/usr/bin/env python3
import os
import subprocess
import pandas as pd
from io import StringIO
import json
import numpy as np
from json import JSONEncoder
import multiprocessing as mp

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def get_lumi(run):
    output = subprocess.check_output(f'brilcalc trg --prescale -c web -r {run} --output-style csv', shell=True)
    return pd.read_csv(StringIO(output.decode()))

def get_data(run, trig):
    output = subprocess.check_output(f'brilcalc trg --prescale -c web -r {run} --hltpath "{trig}_v*" --output-style csv', shell=True).decode()
    if "No hltpathl1seed mapping found" in output:
        return None
    return pd.read_csv(StringIO(output))

def get_run_info(run):
    print(run)
    run_info = {}
    lumis = get_lumi(run)["cmsls"].to_numpy()

    if np.isnan(lumis[0]):
        run_info["lumi"] = [1]
        run_info["bad"] = 'true'
        run_info["1"] = np.ones(ntrigs, dtype=int)
        return run_info


    run_info["lumi"] = lumis
    for lumi in lumis:
        run_info[str(lumi)] = np.zeros(ntrigs, dtype=int)

    for i, trig in enumerate(trigs):
        df = get_data(run, trig)
        if df is None:
            continue
        for pair in df[["cmsls", "totprescval"]].to_numpy():
            run_info[str(pair[0])][i] = pair[1]

    return run_info

trigs = ['HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30',
         'HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30',
         'HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30',
         'HLT_Mu8_TrkIsoVVL',
         'HLT_Mu17_TrkIsoVVL']
ntrigs = len(trigs)
year = 2018

with open(f"{year}_golden.json") as f:
    j = json.load(f)
runs = j.keys()

output = dict()
output["trigs"] = trigs

print(len(runs))

with mp.Pool(15) as pool:
    run_infos = pool.map(get_run_info, list(runs))

for run, run_info in zip(runs, run_infos):
    output[run] = run_info


# print(len(runs))
# for run in runs:
#     print(run)
#     lumis = get_lumi(run)["cmsls"].to_numpy()
#     run_info = {}
#     run_info["lumi"] = lumis
#     for lumi in lumis:
#         run_info[str(lumi)] = np.zeros(ntrigs, dtype=int)

#     for i, trig in enumerate(trigs):
#         df = get_data(run, trig)
#         for pair in df[["cmsls", "totprescval"]].to_numpy():
#             run_info[str(pair[0])][i] = pair[1]
#     output[str(run)] = run_info

json_object = json.dumps(output, cls=NumpyArrayEncoder)
with open(f"prescale_{year}.json", "w") as f:
    f.write(json_object)
    f.write("\n")
