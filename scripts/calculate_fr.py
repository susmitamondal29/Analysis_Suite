#!/usr/bin/env python3
import uproot4 as uproot
import awkward1 as ak
import boost_histogram as bh
import argparse
from collections import OrderedDict
from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt



from analysis_suite.commons.configs import get_metadata
from analysis_suite.commons.histogram import Histogram
from analysis_suite.Plotting.stack import Stack
from analysis_suite.Variable_Creator.vargetter import VarGetter
from analysis_suite.commons.plot_utils import ratio_plot, setup_mplhep
from analysis_suite.commons.info import GroupInfo, PlotInfo

VarGetter.add_part_branches(["LooseMuon", "TightMuon"],
                            ["pt", "phi", "eta", "syst_bitMap"])
VarGetter.add_var_branches(["Met", "Met_phi", "event"])

hep = setup_mplhep()


# nloose_pt = {group: nloose[group].project(0) for group in groups}
# ntight_pt = {group: ntight[group].project(0) for group in groups}


def fit_template(data, qcd, ewk):
    def log_gamma(val):
        return val*np.log(val)-val+0.5*np.log(2*np.pi/val)


    def likelihood(factors, data, qcd, ewk):
        mc = factors[0]*qcd + factors[1]*ewk
        return np.sum(data) + np.sum(log_gamma(mc) - mc*np.log(data))

    start_val = np.sum(data)/(np.sum(qcd+ewk))
    res = minimize(likelihood, (start_val, start_val), args=(data, qcd, ewk), method='Nelder-Mead')
    return res.x


def get_loose(f, mem, part, syst=0):
    vargetter = VarGetter(f, "Nonprompt_FR", mem, syst)
    return (vargetter.pt(f"Loose{part}", 0), vargetter.abseta(f"Loose{Part}", 0),
            {"weight": vargetter.scale})

def get_tight(f, mem, part, syst=0):
    vargetter = VarGetter(f, "Nonprompt_FR", mem, syst)
    return (vargetter.pt(f"Tight{part}", 0), vargetter.abseta(f"Tight{Part}", 0),
            {"weight": vargetter.scale})

def get_mt(f, mem, part, syst=0):
    vargetter = VarGetter(f, "Nonprompt_FullMt", mem, syst)
    return ((vargetter.mt(f"Tight{part}", 0)), vargetter.scale)



# def fill_histograms(filename, year, color_by_group, info, nloose, ntight, mt_shape):
#     with uproot.open(filename) as f:
#         dirs = [d for d, cls in f.iterclassnames() if cls == "TDirectory"]
#         syst = 0
#         for group in color_by_group.keys():
#             for member in info.get_memberMap()[group]:
#                 print(member)
#                 isData = member == "data"
#                 lumi = PlotInfo.lumi[year]*1000 if not isData else 1

#                 fr_region = VarGetter(f, "Nonprompt_FR", member, syst)
#                 mt_region = VarGetter(f, "Nonprompt_FullMt", member, syst)
#                 print(lumi*sum(mt_region.scale))

#                 nloose[group].fill(fr_region.pt("LooseMuon", 0), fr_region.abseta("LooseMuon", 0), weight=lumi*fr_region.scale)
#                 ntight[group].fill(fr_region.pt("TightMuon", 0), fr_region.abseta("TightMuon", 0), weight=lumi*fr_region.scale)
#                 mt_shape[group].fill(mt_region.mt("LooseMuon", 0), weight=lumi*mt_region.scale)

#     for group, mt in mt_shape.items():
#         mt.set_plot_details(info)

def fill_histogram(filename, year, group, info, func, hist):
    lumi = PlotInfo.lumi[year]*1000 if group != "data" else 1
    with uproot.open(filename) as f:
        for member in info.get_memberMap()[group]:
            print(member)
            vals, weight = func(f, member, "Muon")
            hist.fill(vals, weight=lumi*weight)
    hist.set_plot_details(info)

def fill_histograms(filename, year, group, info, func, hist_dict):
    lumi = PlotInfo.lumi[year]*1000 if group != "data" else 1
    with uproot.open(filename) as f:
        for member in info.get_memberMap()[group]:
            print(member)
            vals, weight = func(f, member, "Muon")
            hist_dict[group].fill(vals, weight=lumi*weight)

    hist_dict[group].set_plot_details(info)


def main(year, args):
    color_by_group = OrderedDict({
        "data": "black",
        "qcd_mu": "grey",
        "ewk": "orange",
    })
    mc_groups = ["ewk", "qcd_mu"]

    info = GroupInfo(color_by_group)

    ptbins = bh.axis.Variable([15, 20, 25, 35, 50, 70, 90])
    etabins = bh.axis.Variable([0.0, 1.2, 2.1, 2.4])
    mtbins = bh.axis.Regular(20, 0, 200)
    nloose = {group: Histogram("loose", ptbins, etabins) for group in mc_groups}
    ntight = {group: Histogram("tight", ptbins, etabins) for group in mc_groups}
    mt_shape = {group: Histogram(group, mtbins) for group in mc_groups}
    mt_data = Histogram("data", mtbins)

    fill_histogram(f"fr_data_{year}.root", year, "data", info, get_mt, mt_data)
    for group in mc_groups:
        fill_histograms(f"fr_mc_{year}.root", year, group, info, get_mt, mt_shape)

    mt_stack = Stack(mtbins)
    for group, mt in mt_shape.items():
        mt_stack += mt

    with ratio_plot("mt_unfit", '$M_{T}(\mu)$', mt_stack.get_xrange()) as ax:
        ratio = Histogram("Ratio", mtbins, color="black")
        band = Histogram("Ratio", mtbins, color="plum")
        error = Histogram("Stat Errors", mtbins, color="plum")

        ratio += mt_data/mt_stack
        band += mt_stack/mt_stack
        for hist in mt_stack.stack:
            error += hist

        pad, subpad = ax

        #upper pad
        mt_stack.plot_stack(pad)
        mt_data.plot_points(pad)
        error.plot_band(pad)

        # ratio pad
        ratio.plot_points(subpad)
        band.plot_band(subpad)

        hep.cms.label(ax=pad, lumi=PlotInfo.lumi[year])

    with ratio_plot("mt_fit", '$M_{T}(\mu)$', mt_stack.get_xrange()) as ax:
        qcd_f, ewk_f = fit_template(mt_data.vals, mt_shape["qcd_mu"].vals, mt_shape["ewk"].vals)
        mt_stack["qcd_mu"].scale(qcd_f, changeName=True)
        mt_stack["ewk"].scale(ewk_f, changeName=True)


        ratio = Histogram("Ratio", mtbins, color="black")
        band = Histogram("Ratio", mtbins, color="plum")
        error = Histogram("Stat Errors", mtbins, color="plum")

        ratio += mt_data/mt_stack
        band += mt_stack/mt_stack
        for hist in mt_stack.stack:
            error += hist

        pad, subpad = ax

        #upper pad
        mt_stack.plot_stack(pad)
        mt_data.plot_points(pad)
        error.plot_band(pad)

        # ratio pad
        ratio.plot_points(subpad)
        band.plot_band(subpad)

        hep.cms.label(ax=pad, lumi=PlotInfo.lumi[year])




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")
    args = parser.parse_args()

    for year in args.years:
        main(year, args)
