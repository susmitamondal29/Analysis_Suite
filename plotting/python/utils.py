#!/usr/bin/env python3
import numpy as np
import uproot

analysis_suite.commons.user as user

@np.vectorize
def likelihood_sig(s, b):
    return np.sqrt(2*(s+b)*np.log(1+s/(b+1e-5))-2*s)

def get_syst_index(filename, systName):
    with uproot.open(filename) as f:
        syst_dir = [key for key in f.keys() if "Systematics" in key][0]
        systNames = [name.member("fName") for name in f[syst_dir]]
    if systName not in systNames:
        return -1
    else:
        return systNames.index(systName)

def get_plot_area(name, path=None):
    www_path = user.www_area/name
    if path:
        www_path /= path.stem
    www_path /= time.strftime("%Y_%m_%d")
    return www_path

def make_plot_paths(path):
    (path/"plots").mkdir(exist_ok=True, parents=True)
    (path/"logs").mkdir(exist_ok=True, parents=True)
