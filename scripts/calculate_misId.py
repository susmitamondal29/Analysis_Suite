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
from analysis_suite.commons.info import FileInfo, GroupInfo, PlotInfo
from fake_rate_helper import setup_events, setup_histogram, setup_plot, mask_vg, get_fake_rate, DataInfo, GraphInfo, hep

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


def misid_measure(year, lumi, ginfo, finfo, args):
    Path(f'MR_{year}').mkdir(exist_ok=True)

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

    mc_info = DataInfo(Path(f"misId_mc_{year}.root"), year)
    mc_info.setup_member(ginfo, finfo, "DY_ht")
    mc_info.setup_member(ginfo, finfo, "ttbar_lep")

    data_info = DataInfo(Path(f"misId_data_{year}.root"), year)
    data_info.setup_member(ginfo, finfo, "data")

    mr_data = setup_events(data_info, "OS_MR")['data']
    mr_mc = setup_events(mc_info, "OS_MR")

    chan_masks = {"MM": lambda vg: vg.TightMuon.num() == 2,
                  "EE": lambda vg: vg.TightElectron.num() == 2,
                  "EM": lambda vg: num_two_parts(vg.TightMuon, vg.TightElectron),
                  }

    for chan in args.mr_chan:
        name = f'MR_{year}/{chan}_{year}'

        # Masking
        mask_vg(mr_mc, chan_masks[chan])
        mask_vg(mr_data, chan_masks[chan])

        for graph in [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met]:
            setup_plot(mr_mc, mr_data, chan, graph, name, "MR")

    outdir = f"MR_{year}"

    mask_vg(mr_mc, lambda vg: vg.TightElectron.num() > 0)
    mask_vg(mr_data, lambda vg: vg.TightElectron.num() > 0)

    flip_hist = setup_histogram("", {mem: hist for vgs in mr_mc.values() for mem, hist in vgs.items()},"", flip_pteta)
    all_hist = setup_histogram('data', mr_data, "", all_pteta)
    fr = Histogram.efficiency(flip_hist, all_hist)
    fr_plot(f'{outdir}/fr_{year}', fr, year)
    print(fr.vals)

    with plot(f'{outdir}/fr_pt_{year}') as ax:
        flip_pt = flip_hist.project(0)
        all_pt = all_hist.project(0)
        fr_pt = Histogram.efficiency(flip_pt, all_pt)
        fr_pt.plot_points(ax)
        ax.set_xlabel("$p_{T}(e)$")
        hep.cms.label(ax=ax, lumi=lumi)

    with plot(f'{outdir}/fr_eta_{year}') as ax:
        flip_eta = flip_hist.project(1)
        all_eta = all_hist.project(1)
        fr_eta = Histogram.efficiency(flip_eta, all_eta)
        fr_eta.plot_points(ax)
        ax.set_xlabel("$\eta(e)$")
        hep.cms.label(ax=ax, lumi=lumi)

    # Dump fake rate
    with open(f"charge_misid_rate_{year}.pickle", "wb") as f:
        pickle.dump(fr.hist, f)


def misid_closure(year, lumi, ginfo, finfo, args):
    Path(f'CR_{year}').mkdir(exist_ok=True)

    pt_lead = GraphInfo("pt_lead", '$p_{{T}}(e_{{lead}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : vg.TightElectron.get_hist('pt', 0))
    pt_sublead = GraphInfo("pt_sub", '$p_{{T}}(e_{{sub}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : vg.TightElectron.get_hist('pt', 1))
    pt_all = GraphInfo("pt_all", '$p_{{T}}(e)$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_all(vg, chan, 'pt'))
    eta_lead = GraphInfo("eta_lead", '$\eta(e_{{lead}})$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : vg.TightElectron.get_hist('eta', 0))
    eta_sublead = GraphInfo("eta_sub", '$\eta(e_{{sub}})$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : vg.TightElectron.get_hist('eta', 0))
    eta_all = GraphInfo("eta_all", '$\eta(e)$', bh.axis.Regular(25, -2.5, 2.5), lambda vg, chan : get_all(vg, chan, 'eta'))
    mass = GraphInfo("mass", '$M(e, e)$', bh.axis.Regular(20, 70, 115), lambda vg, chan : vg.TightElectron.get_hist('mass', 0, vg.TightElectron, 1))
    ht = GraphInfo("ht", 'HT', bh.axis.Regular(30, 0, 250), lambda vg, chan : vg.get_hist("HT"))
    met = GraphInfo("met", 'MET', bh.axis.Regular(30, 0, 50), lambda vg, chan : vg.get_hist("Met"))

    mc_info = DataInfo(Path(f"misId_mc_{year}.root"), year)
    mc_info.setup_member(ginfo, finfo, "DY")
    mc_info.setup_member(ginfo, finfo, "ttbar_lep")

    data_info = DataInfo(Path(f"misId_data_{year}.root"), year)
    data_info.setup_member(ginfo, finfo, "data")

    os_data = setup_events(data_info, "OS_CR")['data']
    os_mc = setup_events(mc_info, "OS_CR")
    ss_data = setup_events(data_info, "SS")['data']
    ss_mc = setup_events(mc_info, "SS")

    chan = 'EE'
    name = f'CR_{year}/Closure'

    # OS Region data/mc (real data) (where flip happens)
    for graph in [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met]:
        setup_plot(os_mc, os_data, chan, graph, name, 'OS')

    # Closure Region data/mc (real data)
    for graph in [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met]:
        setup_plot(ss_mc, ss_data, chan, graph, name, 'SS')

    # Closure Region data/mc (real data)
    with open(f"charge_misid_rate_{year}.pickle", "rb") as f:
        fake_rates = pickle.load(f)
    scale_misId(os_data['data'], fake_rates)
    flip_SS_vg = {"charge_flip": os_data}
    for graph in [pt_lead, pt_sublead, pt_all, eta_lead, eta_sublead, eta_all, mass, ht, met]:
        setup_plot(flip_SS_vg, ss_data, chan, graph, f'{name}_flip','SS')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")
    parser.add_argument("--mr_chan", default='all',
                        type=lambda x: ['MM', 'EM', 'EE'] if x == 'all' \
                                   else [i.strip() for i in x.split(',')],
                        help="Channels for the fake")
    args = parser.parse_args()

    color_by_group = {
        "data": "black",
        "DY_ht": "goldenrod",
        "DY": "goldenrod",
        "ttbar_lep": 'royalblue',
        'charge_flip': 'seagreen',
    }
    ginfo = GroupInfo(color_by_group)
    GraphInfo.info = ginfo


    for year in args.years:
        lumi = PlotInfo.lumi[year]
        GraphInfo.lumi = lumi
        finfo = FileInfo(year)

        misid_measure(year, lumi, ginfo, finfo, args)
        misid_closure(year, lumi, ginfo, finfo, args)
