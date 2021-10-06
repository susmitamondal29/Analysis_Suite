#!/usr/bin/env python3
import uproot4 as uproot
from analysis_suite.commons.histogram import Histogram
import boost_histogram as bh
import numpy as np
import logging


def getNormedHistos(infilename, file_info, plot_info, histName, year):
    groupHists = dict()
    ak_col = plot_info.at(histName, "Column")

    size = 5
    start, end = 0, 5
    width = (end - start)/size
    cr_list = [create_W_CR]
    cr_bins = [start-(i+1)*width for i in range(len(cr_list))]

    binning = get_binning(size, start, end, len(cr_list))

    with uproot.open(infilename) as f:
        for group, members in file_info.group2MemberMap.items():
            groupHists[group] = Histogram(group, binning)
            for mem in members:
                if mem not in f:
                    logging.warning(f'Could not find sample {mem} in file for year {year}')
                    continue
                if ak_col not in f[mem]:
                    logging.error(f"Could not find variable {histName} in file for year {year}")
                    raise ValueError()
                arrays = f[mem].arrays()

                groupHists[group].fill(*create_SR(arrays, "NBJets"))
                for cr_bin, cr_func in zip(cr_bins, cr_list):
                    groupHists[group].fill(*cr_func(arrays, cr_bin))
            groupHists[group].scale(plot_info.get_lumi(year)*1000)

    return groupHists

def get_binning(nbins, start, end, nCR):
    width = (end - start)/nbins
    return bh.axis.Regular(nbins+nCR, start-width*nCR, end)


def create_SR(array, varname):
    mask = array.Signal >= 0.65
    new_array = array[mask]
    return (new_array[varname], new_array.scale_factor)

def create_W_CR(array, cr_value):
    mask = array.Signal < 0.65
    return (np.ones(np.sum(mask))*cr_value, array.scale_factor[mask])

def create_Z_CR(array):
    pass
