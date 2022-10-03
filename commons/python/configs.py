#!/usr/bin/env python3
import numpy as np
import uproot
import sys
from importlib import import_module

from .user import analysis_area
if str(analysis_area) not in sys.path:
    sys.path.append(str(analysis_area))

def get_inputs(workdir):
    return import_module('.inputs', f'workspace.{workdir.stem}')

def get_ntuple(name, obj='info'):
    module = import_module(f'.{name}', 'ntuple_info')
    return getattr(module, obj)

def get_list_systs(infile, tool, systs=["all"], **kwargs):
    allSysts = set()
    if tool == 'flatten':
        if infile.is_dir():
            all_files = list(infile.glob('*root'))
        else:
            all_files = [infile]

        def get_systs(tlist):
            return np.unique([item.member('fName') for item in tlist])

        for file_ in all_files:
            with uproot.open(file_) as f:
                for key in f.keys() :
                    if "Systematics" not in key:
                        continue
                    allSysts |= set(get_systs(f[key]))
    elif tool == 'mva':
        for f in infile.glob("**/processed*root"):
            allSysts |= {"_".join(f.stem.split('_')[1:-1])}
    elif tool == 'combine':
        for f in infile.glob("**/test*root"):
            allSysts |= {"_".join(f.stem.split('_')[1:-1])}

    if systs != ['all']:
        finalSysts = list()
        for syst in systs:
            if f'{syst}_up' in allSysts and f'{syst}_down' in allSysts:
                finalSysts += [f'{syst}_up', f'{syst}_down']
            elif syst == "Nominal":
                finalSysts.append("Nominal")
        allSysts = set(finalSysts)
    return allSysts

def sig_fig(x, p=3):
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags

@np.vectorize
def asymptotic_sig(s, b):
    return s/np.sqrt(b+1e-5)

