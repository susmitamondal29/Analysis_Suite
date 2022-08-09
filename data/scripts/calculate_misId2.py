#!/usr/bin/env python3
import boost_histogram as bh
import argparse
from scipy.optimize import minimize
import numpy as np
import awkward as ak;
import pickle
from pathlib import Path
from matplotlib import colors

from analysis_suite.commons.histogram import Histogram
from analysis_suite.commons.plot_utils import plot, plot_colorbar
from analysis_suite.commons.info import fileInfo, GroupInfo
from analysis_suite.commons.constants import lumi
from analysis_suite.Plotting.plotter import GraphInfo
from analysis_suite.commons.fake_rate_helper import setup_events, setup_histogram, setup_plot, mask_vg, get_fake_rate, hep, plot_project, add_histgroups

def num_two_parts(part1, part2):
    return (part1.num() == 1)*(part2.num() == 1)

def get_all(vg, chan, var):
    if chan == "MM":
        p1_var, scale = vg["TightMuon"].get_hist(var, 0)
        p2_var = vg['TightMuon'][var, 1]
    elif chan == "EE":
        p1_var, scale = vg[f"TightElectron"].get_hist(var, 0)
        p2_var = vg['TightElectron'][var, 1]
    else:
        p1_var, scale = vg[f"TightMuon"].get_hist(var, 0)
        p2_var = vg['TightElectron'][var, 0]

    return np.concatenate((p1_var, p2_var)), np.concatenate((scale, scale))

def get_lead(vg, chan, var):
    if chan == "MM":
        return vg["TightMuon"].get_hist(var, 0)
    elif chan == "EE":
        return vg["TightElectron"].get_hist(var, 0)
    else:
        e_var, scale = vg["TightElectron"].get_hist(var, 0)
        m_var = vg["TightMuon"][var, 0]
        m_vs_e = vg["TightMuon"]["pt",0] > vg["TightElectron"]["pt",0]
        return np.where(m_vs_e, m_var, e_var), scale

def get_sublead(vg, chan, var):
    if chan == "MM":
        return vg["TightMuon"].get_hist(var, 1)
    elif chan == "EE":
        return vg["TightElectron"].get_hist(var, 1)
    else:
        e_var, scale = vg["TightElectron"].get_hist(var, 0)
        m_var = vg["TightMuon"][var, 0]
        m_vs_e = vg["TightMuon"]["pt",0] < vg["TightElectron"]["pt",0]
        return np.where(m_vs_e, m_var, e_var), scale

def get_mass(vg, chan):
    part1 = vg.TightMuon if chan[0] == "M" else vg.TightElectron
    part2 = vg.TightMuon if chan[1] == "M" else vg.TightElectron
    idx2 = 0 if chan == "EM" else 1
    return part1.get_hist('mass', 0, part2, idx2)

def fr_plot(name, hist, year, **kwargs):
    with plot(name, figsize=(18, 10)) as ax:
        # mesh = hist.plot_2d(ax, **kwargs)
        xx = np.tile(hist.axes[0].edges, (len(hist.axes[1])+1, 1))
        yy = np.tile(hist.axes[1].edges, (len(hist.axes[0])+1, 1)).T
        mesh = ax.pcolormesh(xx, yy, hist.vals.T, norm=colors.LogNorm(vmin=1e-5, vmax=1e-2),
                             shading='flat', cmap="Blues", **kwargs)
        for j, y in enumerate(hist.axes[1].centers):
            for i, x in enumerate(hist.axes[0].centers):
                ytot = y
                val_str = f'{hist.vals[i,j]:.2e}\n$\pm${hist.err[i,j]:.2e}'
                text = ax.text(x, ytot, val_str, fontsize='xx-small', ha="center", va='center')
        ax.set_title("Electron Charge MisId Rate")
        ax.set_xlabel("$p_{T}(e)$ [GeV]")
        ax.set_ylabel("$|\eta(e)|$")
        hep.cms.label(ax=ax, year=year)
        plot_colorbar(mesh, ax, barpercent=2)

def flip_data(part, flip=False):
    if flip:
        flip_mask = ak.flatten(part.flip == 1)
        return (ak.flatten(part.pt)[flip_mask], ak.flatten(np.abs(part.eta))[flip_mask]), ak.flatten(part.scale(-1))[flip_mask]
    else:
        return (ak.flatten(part.pt), ak.flatten(np.abs(part.eta))), ak.flatten(part.scale(-1))

def scale_misId(vg, fake_rate):
    part = vg.TightElectron
    fr1 = get_fake_rate(part, fake_rate, 0)
    fr2 = get_fake_rate(part, fake_rate, 1)
    vg.scale = (fr1/(1-fr1)+fr2/(1-fr2))*vg.scale


def measure(files, ginfo, year):
    plot_dir = Path(f'MR_{year}')
    plot_dir.mkdir(exist_ok=True)

    ptbins = bh.axis.Variable([15, 40, 60, 80, 100, 200, 300])
    etabins = bh.axis.Variable([0.0, 0.8, 1.479, 2.5])

    pt_lead = GraphInfo("pt_lead", '$p_{{T}}(lep_{{lead}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_lead(vg, chan, "pt"))
    pt_sublead = GraphInfo("pt_sub", '$p_{{T}}(lep_{{sub}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_sublead(vg, chan, 'pt'))
    pt_all = GraphInfo("pt_all", '$p_{{T}}(lep)$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_all(vg, chan, 'pt'))
    eta_lead = GraphInfo("eta_lead", '$\eta(lep_{{lead}})$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : get_lead(vg, chan, "eta"))
    eta_sublead = GraphInfo("eta_sub", '$\eta(lep_{{sub}})$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : get_sublead(vg, chan, 'eta'))
    eta_all = GraphInfo("eta_all", '$\eta(lep)$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : get_all(vg, chan, 'eta'))
    mass = GraphInfo("mass", '$M({})$', bh.axis.Regular(30, 0, 400), lambda vg, chan : get_mass(vg, chan))
    ht = GraphInfo("ht", 'HT', bh.axis.Regular(30, 250, 1000), lambda vg, chan : vg.get_hist("HT"))
    met = GraphInfo("met", 'MET', bh.axis.Regular(30, 25, 250), lambda vg, chan : vg.get_hist("Met"))
    flip_pteta = GraphInfo("flip_pteta", "", (ptbins, etabins), lambda vg, chan: flip_data(vg.TightElectron, flip=True))
    all_pteta = GraphInfo("all_pteta", "", (ptbins, etabins), lambda vg, chan: flip_data(vg.TightElectron, flip=False))
    graphs = [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met]
    all_graphs = [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met, flip_pteta, all_pteta]

    groups = setup_groups(["data", "DY_ht", "ttbar_lep", "VV"], ginfo)
    chans = ["MM", "EE", "EM"]
    masks = {"MM": lambda vg: vg.TightMuon.num() == 2,
             "EE": lambda vg: vg.TightElectron.num() == 2,
             "EM": lambda vg: np.all((vg.TightMuon.num() == 1, vg.TightElectron.num() == 1, vg["HLT_emu"]==1)),
             }

    out_hists = fill_histograms(files, masks, all_graphs, groups, chans, "OS_MR", lumi[year]*1000)
    set_plot_details(out_hists, ginfo)

    for chan in chans
        filename = plot_dir / f'{chan}_{year}'
        for graph in graphs:
            make_plot(out_hists[graph.name][chan], graph, chan, lumi[year], filename, "MR")

    flip_hist = Histogram("flip", *flip_pteta.bins())
    all_hist = Histogram("all", *all_pteta.bins())
    for chan in ["EE", "EM"]:
        for group in groups.keys():
            if group == "data": continue
            flip_hist += out_hists["flip_pteta"][chan][group]
            all_hist += out_hists["all_pteta"][chan][group]

    print(flip_hist.vals)
    print(all_hist.vals)
    fr = Histogram.efficiency(flip_hist, all_hist)
    fr_plot(f'{outdir}/fr_{year}', fr, year)
    print(fr.vals)

    plot_project(f'{outdir}/fr_pt_{year}', flip_hist, all_hist, 0, "$p_{T}(e)$", lumi[year])
    plot_project(f'{outdir}/fr_eta_{year}', flip_hist, all_hist, 1, "$\eta(e)$", lumi[year])

    # Dump fake rate
    with open(f"charge_misid_rate_{year}.pickle", "wb") as f:
        pickle.dump(fr.hist, f)


def misid_closure(files, ginfo, year):
    plot_dir = Path(f'CR_{year}')
    plot_dir.mkdir(exist_ok=True)

    pt_lead = GraphInfo("pt_lead", '$p_{{T}}(e_{{lead}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : vg.TightElectron.get_hist('pt', 0))
    pt_sublead = GraphInfo("pt_sub", '$p_{{T}}(e_{{sub}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : vg.TightElectron.get_hist('pt', 1))
    pt_all = GraphInfo("pt_all", '$p_{{T}}(e)$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_all(vg, chan, 'pt'))
    eta_lead = GraphInfo("eta_lead", '$\eta(e_{{lead}})$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : vg.TightElectron.get_hist('eta', 0))
    eta_sublead = GraphInfo("eta_sub", '$\eta(e_{{sub}})$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : vg.TightElectron.get_hist('eta', 0))
    eta_all = GraphInfo("eta_all", '$\eta(e)$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : get_all(vg, chan, 'eta'))
    mass = GraphInfo("mass", '$M(e, e)$', bh.axis.Regular(20, 70, 115), lambda vg, chan : vg.TightElectron.get_hist('mass', 0, vg.TightElectron, 1))
    ht = GraphInfo("ht", 'HT', bh.axis.Regular(30, 0, 250), lambda vg, chan : vg.get_hist("HT"))
    met = GraphInfo("met", 'MET', bh.axis.Regular(30, 0, 50), lambda vg, chan : vg.get_hist("Met"))
    graphs = [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met]

    groups = setup_groups(["data", "DY", "ttbar_lep", "VV"], ginfo)
    chans = ["EE"]
    masks = { "EE": lambda vg: vg.TightElectron.num() == 2 }

    # Closure Region data/mc (real data)
    with open(f"charge_misid_rate_{year}.pickle", "rb") as f:
        fake_rates = pickle.load(f)

    scaler = lambda vg : scale_misId(vg, fake_rates)

    os_hists = fill_histograms(files, masks, graphs, groups, chans, "OS_CR", lumi*1000)
    ss_hists = fill_histograms(files, masks, graphs, groups, chans, "SS", lumi*1000)
    flipped_hists = fill_histograms(files, masks, graphs, {"charge_flip": ["data"]}, chans, "OS", lumi[year]*1000, scaler=scaler)
    add_histgroups(flipped_hists, ss_hists, ['data'])

    set_plot_details(out_hists, ginfo)

    for chan in chans
        filename = plot_dir / f'{chan}_{year}'
        for graph in graphs:
            make_plot(os_hists[graph.name][chan], graph, chan, lumi[year], filename, "OS")
            make_plot(ss_hists[graph.name][chan], graph, chan, lumi[year], filename, "SS")
            make_plot(flipped_hists[graph.name][chan], graph, chan, lumi[year], filename, "SS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', default='misId')
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")
    args = parser.parse_args()

    color_by_group = {
        "data": "black",
        "DY_ht": "goldenrod",
        "DY": "goldenrod",
        "ttbar_lep": 'royalblue',
        "VV": 'mediumorchid',
        'charge_flip': 'seagreen',
    }
    ginfo = GroupInfo(color_by_group)

    for year in args.years:
        files = list()
        files = [f"{args.filename}_data_{year}.root"]
        # files.extend(get_files(year, "fake_rate", "data"))
        files.extend(get_files(args.filename, year))

        # measurement(files, ginfo, year)
        closure(files, ginfo, year)
