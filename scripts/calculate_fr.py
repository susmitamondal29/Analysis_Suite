#!/usr/bin/env python3
import boost_histogram as bh
import argparse
from scipy.optimize import minimize
import numpy as np
import pickle
from pathlib import Path

from analysis_suite.commons.histogram import Histogram
from analysis_suite.commons.plot_utils import plot, plot_colorbar
from analysis_suite.commons.constants import lumi
from analysis_suite.commons.info import GroupInfo
from analysis_suite.commons.fake_rate_helper import GraphInfo, hep, fill_histograms, get_dirnames, get_by_val, setup_groups, make_plot, set_plot_details, get_fake_rate, plot_project, add_histgroups


def get_files(filename, year):
     path = (Path.home() / f"hdfs/workspace/{filename}").resolve()
     return list(path.glob(f"*{year}.root"))


trig_scale = {
    # "2016": {
    #     "Electron" : [0.8670, 1.0125],
    #     "Muon" : [0.7023, 0.9768],
    # },
    # "2017": {
    #     "Electron" : [0.9540, 1.1406],
    #     "Muon" : [0.7123, 1.0358],
    # },
    # "2018": {
    #     "Electron" : [0.9491, 1.1130],
    #     "Muon" : [0.9074, 1.1205],
    # },
    "2016": {
        "Electron" : [1., 1.],
        "Muon" : [1., 1.],
    },
    "2017": {
        "Electron" : [1., 1.],
        "Muon" : [1., 1.],
    },
    "2018": {
        "Electron" : [1., 1.],
        "Muon" : [1., 1.],
    },
}

def fit_template(data, qcd, ewk, fit_type="chi2"):
    def log_gamma(val):
        return val*np.log(val)-val+0.5*np.log(2*np.pi/val)

    def likelihood(factors, data, qcd, ewk):
        mc = factors[0]*qcd + factors[1]*ewk
        return np.sum(data) + np.sum(log_gamma(mc) - mc*np.log(data))

    def chi2(factors, data, qcd, ewk):
        mc = qcd.hist*factors[0] + ewk.hist*factors[1]
        tot_diff2 = (data.vals - mc.view().value)**2
        return np.sum(tot_diff2/data.err)

    start_val = np.sum(data.vals)/(np.sum(qcd.vals+ewk.vals))
    if fit_type == "chi2":
        res = minimize(chi2, (start_val, start_val), args=(data, qcd, ewk), method='Nelder-Mead')
    elif fit_type == "ml":
        res = minimize(likelihood, (start_val, start_val), args=(data.vals, qcd.vals, ewk.vals), method='Nelder-Mead')
    return res.x

def scale_trigger(vg, chan, trig_scale, ptCut):
    pt = np.where(vg[f'Fake{chan}'].num() == 1, vg[f"Fake{chan}"].pad('pt', 0), vg[f"Tight{chan}"].pad('pt', 0))
    lowpt_weight = (pt < ptCut)*trig_scale[0]
    highpt_weight = (pt > ptCut)*trig_scale[1]
    vg.scale = (lowpt_weight+highpt_weight)*vg.scale

def scale_fake(vg, chan, fakerate):
    part = vg[f'Fake{chan}']
    fr = get_fake_rate(part, fakerate, 0)
    mask = part.num() > 0

    print(sum(mask))
    print(sum(vg.scale[mask]))
    print(sum(vg.scale[mask]*fr/(1-fr)))

    vg.scale = (fr/(1-fr), mask)
    print(sum(vg.scale))


def fr_plot(name, tight, loose, part, **kwargs):
    with plot(name) as ax:
        mesh = (tight/loose).plot_2d(ax, **kwargs)
        ax.set_xlabel(f"$p_{{T}}({part})$ [GeV]")
        ax.set_ylabel(f"$|\eta({part})|$")
        plot_colorbar(mesh, ax)

def get_fake(vg, chan, var):
    return vg[f"Fake{chan}"].get_hist(var, 0)

def get_tight(vg, chan, var):
    return vg[f"Tight{chan}"].get_hist(var, 0)

def get_all(vg, chan, var):
    fake_var, fake_scale = vg[f"Fake{chan}"].get_hist(var, 0)
    tight_var, tight_scale = vg[f"Tight{chan}"].get_hist(var, 0)
    return np.concatenate((fake_var, tight_var)), np.concatenate((fake_scale, tight_scale))

def get_all_pteta(vg, chan):
    (fake_pt, fake_eta), fake_scale = vg[f"Fake{chan}"].get_hist2d('pt', 'abseta', 0)
    (tight_pt, tight_eta), tight_scale = vg[f"Tight{chan}"].get_hist2d('pt', 'abseta', 0)
    return (np.concatenate((fake_pt, tight_pt)), np.concatenate((fake_eta, tight_eta))), np.concatenate((fake_scale, tight_scale))

def num_two_parts(part1, part2):
    return (part1.num() == 1)*(part2.num() == 1)

def measurement(files, ginfo, year):
    plot_dir = Path(f'MR_{year}')
    plot_dir.mkdir(exist_ok=True)

    ptbins = bh.axis.Variable([15, 20, 25, 35, 50])
    etabins = bh.axis.Variable([0.0, 1.2, 2.1, 2.5])

    pt_loose = GraphInfo("loosept", '$p_{{T}}({}_{{loose}})$', bh.axis.Regular(20, 0, 150), lambda vg, chan : get_all(vg, chan, 'pt'))
    pt_tight = GraphInfo("tightpt", '$p_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_tight(vg, chan, "pt"))
    mt_loose = GraphInfo("loosemt", '$M_{{T}}({}_{{loose}})$', bh.axis.Regular(20, 0, 20), lambda vg, chan : get_all(vg, chan, 'mt'))
    mt_tight = GraphInfo("tightmt", '$M_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 20), lambda vg, chan : get_tight(vg, chan, 'mt'))
    met = GraphInfo("met", '$MET$', bh.axis.Regular(20, 0, 30), lambda vg, chan : vg.get_hist("Met"))
    met_phi = GraphInfo("metphi", '$\phi(MET)$', bh.axis.Regular(20, -np.pi, np.pi), lambda vg, chan : vg.get_hist("Met_phi"))
    pt_eta_all = GraphInfo("loosefr", '', (ptbins, etabins), lambda vg, chan : get_all_pteta(vg, chan))
    pt_eta_tight = GraphInfo("tightfr", '', (ptbins, etabins), lambda vg, chan : vg[f"Tight{chan}"].get_hist2d('pt', 'abseta', 0))

    all_graphs = [# pt_loose, pt_tight, mt_loose, mt_tight, met, met_phi,
                  pt_eta_all, pt_eta_tight]
    graphs = [# pt_loose, pt_tight, mt_loose, mt_tight, met, met_phi
              ]

    groups = setup_groups(["data", "ewk", "qcd"], ginfo)
    chans = ["Electron", "Muon"]
    latex_chan = {"Electron": "e", "Muon": "\mu"}
    mask = {chan: lambda vg : np.any((vg[f'Tight{chan}'].num() == 1, vg[f'Fake{chan}'].num() == 1)) for chan in chans}
    scaler = [
        lambda vg : scale_trigger(vg, "Muon", trig_scale[year]["Muon"], 20),
        lambda vg : scale_trigger(vg, "Electron", trig_scale[year]["Electron"], 25),
    ]

    out_hists = fill_histograms(files, mask, all_graphs, groups, chans, "Measurement", lumi[year]*1000, scaler=scaler)
    set_plot_details(out_hists, ginfo)

    # Load MC scale factors
    with open(f"mc_scales_{year}.pickle", "rb") as f:
        mc_scale_factors = pickle.load(f)

    fake_rates = dict()
    for chan in chans:
        filename = plot_dir / f'{chan}_{year}'
        for graph in graphs:
            make_plot(out_hists[graph.name][chan], graph, chan, lumi[year], filename, "MR")
            for group, sf in mc_scale_factors[chan].items():
                out_hists[graph.name][chan][group].scale(sf, changeName=True)
            make_plot(out_hists[graph.name][chan], graph, chan, lumi[year], f'{filename}_scaled', "MR")

        h_pteta_tight = out_hists['tightfr'][chan]
        h_pteta_all = out_hists['loosefr'][chan]
        for group in h_pteta_tight.keys():
            for i in range(etabins.size):
                h_pteta_tight[group].hist[-1, i] += h_pteta_tight[group].hist[bh.overflow, i]
                h_pteta_all[group].hist[-1, i] += h_pteta_all[group].hist[bh.overflow, i]

        h_pteta_tight['data_ewk'] = h_pteta_tight['data'] - h_pteta_tight['ewk']
        h_pteta_all['data_ewk'] = h_pteta_all['data'] - h_pteta_all['ewk']

        fake_rates[chan] = {
            "qcd": Histogram.efficiency(h_pteta_tight['qcd'], h_pteta_all['qcd']).hist,
            "data": Histogram.efficiency(h_pteta_tight['data'], h_pteta_all['data']).hist,
            "data_ewk": Histogram.efficiency(h_pteta_tight['data_ewk'], h_pteta_all['data_ewk']).hist,
        }
        print(fake_rates[chan]['data_ewk'].values())
        # Fake Rate Plotting
        latex = latex_chan[chan]
        fr_plot(f"{filename}_fr_qcd", h_pteta_tight['qcd'], h_pteta_all['qcd'], latex)
        fr_plot(f"{filename}_fr_data", h_pteta_tight['data'], h_pteta_all['data'], latex)
        fr_plot(f"{filename}_fr_ewkcorr", h_pteta_tight['data_ewk'], h_pteta_all['data_ewk'], latex)

        plot_project(f'{filename}_fr_pt_{year}', h_pteta_tight['data_ewk'], h_pteta_all['data_ewk'], 0, f"$p_{{T}}({latex})$", lumi[year])
        plot_project(f'{filename}_fr_eta_{year}', h_pteta_tight['data_ewk'], h_pteta_all['data_ewk'], 1, f'$\eta({latex})$', lumi[year])

    # Dump Fake rates
    with open(f"fr_{year}.pickle", "wb") as f:
        pickle.dump(fake_rates, f)


def sideband(files, ginfo, year):
    plot_dir = Path(f'SB_{year}')
    plot_dir.mkdir(exist_ok=True)

    pt_tight = GraphInfo("tightpt", '$p_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_tight(vg, chan, "pt"))
    mt_tight = GraphInfo("tightmt", '$M_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_tight(vg, chan, 'mt'))
    met = GraphInfo("met", '$MET$', bh.axis.Regular(20, 30, 200), lambda vg, chan : vg.get_hist("Met"))
    met_phi = GraphInfo("metphi", '$\phi(MET)$', bh.axis.Regular(20, -np.pi, np.pi), lambda vg, chan : vg.get_hist("Met_phi"))
    graphs = [pt_tight, mt_tight, met, met_phi]

    groups = setup_groups(["data", "ewk", "qcd"], ginfo)
    chans = ["Electron", "Muon"]
    mask = {chan: lambda vg : np.any((vg[f'Tight{chan}'].num() == 1, vg[f'Fake{chan}'].num() == 1)) for chan in chans}
    scaler = [
        lambda vg : scale_trigger(vg, "Muon", trig_scale[year]["Muon"], 20),
        lambda vg : scale_trigger(vg, "Electron", trig_scale[year]["Electron"], 25),
    ]

    out_hists = fill_histograms(files, mask, graphs, groups, chans, "SideBand", lumi[year]*1000, scaler=scaler)
    set_plot_details(out_hists, ginfo)

    mc_scale_factors = dict()
    for chan in chans:
        filename = plot_dir / f'{chan}_{year}'
        for graph in graphs:
            make_plot(out_hists[graph.name][chan], graph, chan, lumi[year], filename, "SB")

        # calculate templated fit
        h_tightmt = out_hists["tightmt"][chan]
        qcd_f, ewk_f = fit_template(h_tightmt['data'], h_tightmt['qcd'], h_tightmt["ewk"])
        mc_scale_factors[chan] = {"ewk": ewk_f, 'qcd': qcd_f}
        print(chan, qcd_f, ewk_f)
        for graph in graphs:
            for group, sf in mc_scale_factors[chan].items():
                out_hists[graph.name][chan][group].scale(sf, changeName=True)
            make_plot(out_hists[graph.name][chan], graph, chan, lumi[year], f"{filename}_scaled", "SB")

    # Dump MC scale factors
    with open(f"mc_scales_{year}.pickle", "wb") as f:
        pickle.dump(mc_scale_factors, f)


def closure(files, ginfo, year):
    plot_dir = Path(f'CR_{year}')
    plot_dir.mkdir(exist_ok=True)

    met = GraphInfo("met", '$MET$', bh.axis.Regular(20, 0, 200), lambda vg, chan : vg.get_hist("Met"))
    ht = GraphInfo("ht", '$H_T$', bh.axis.Regular(15, 0, 600), lambda vg, chan : vg.get_hist("HT"))
    njet = GraphInfo("njets", '$N_j$', bh.axis.Regular(8, 0, 8), lambda vg, chan : (vg.Jets.num(), vg.scale))
    nbjet = GraphInfo("nbjets", '$N_b$', bh.axis.Regular(8, 0, 8), lambda vg, chan : (vg.BJets.num(), vg.scale))
    nloosebjet = GraphInfo("nloosebjets", '$N_{{bloose}}$', bh.axis.Regular(8, 0, 8), lambda vg, chan : vg.get_hist("N_bloose"))
    ntightbjet = GraphInfo("ntightbjets", '$N_{{btight}}$', bh.axis.Regular(8, 0, 8), lambda vg, chan : vg.get_hist("N_btight"))
    graphs = [met, ht, njet, nbjet, nloosebjet, ntightbjet]

    # Load MC scale factors
    with open(f"fr_{year}.pickle", "rb") as f:
        fake_rates = pickle.load(f)

    groups = setup_groups(["data", "ttbar_lep", "wjets"], ginfo)
    groups_nodata = setup_groups(["ttbar_lep", "wjets"], ginfo)
    chans = ["MM", "EE", "EM"]
    tt_masks = {"MM": lambda vg: vg.TightMuon.num() == 2,
                "EE": lambda vg: vg.TightElectron.num() == 2,
                "EM": lambda vg: num_two_parts(vg.TightMuon, vg.TightElectron),
                }
    tf_masks = {"MM": lambda vg: num_two_parts(vg.TightMuon, vg.FakeMuon),
                "EE": lambda vg: num_two_parts(vg.TightElectron, vg.FakeElectron),
                "EM": lambda vg: num_two_parts(vg.TightMuon, vg.FakeElectron)+num_two_parts(vg.TightElectron, vg.FakeMuon)
                }
    fr_scaler = [
        lambda vg: scale_fake(vg, "Electron", fake_rates["Electron"]["data_ewk"]),
        lambda vg: scale_fake(vg, "Muon", fake_rates["Muon"]["data_ewk"])
    ]

    hists_TF = fill_histograms(files, tf_masks, graphs, groups, chans, "Closure_TF", lumi[year]*1000)
    set_plot_details(hists_TF, ginfo)

    mc_hists_TT = fill_histograms(files, tt_masks, graphs, groups_nodata, chans, "Closure_TT", lumi[year]*1000)
    hists_TT = fill_histograms(files, tf_masks, graphs, {"nonprompt": ["data"]}, chans, "Closure_TF", 1, scaler=fr_scaler)
    add_histgroups(hists_TT, mc_hists_TT, groups_nodata.keys())
    set_plot_details(hists_TT, ginfo)

    for chan in chans:
        filename = plot_dir / f'{chan}_{year}'
        for graph in graphs:
            make_plot(hists_TF[graph.name][chan], graph, chan, lumi[year], filename, "TF")
            make_plot(hists_TT[graph.name][chan], graph, chan, lumi[year], filename, "TT", data_name="nonprompt")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")

    args = parser.parse_args()

    color_by_group = {
        "data": "black",
        "qcd": "grey",
        "ewk": "orange",
        "wjet_ht": "olive",
        "wjets": "olive",
        "ttbar_lep": "royalblue",
        'nonprompt': 'lightgrey'
    }
    ginfo = GroupInfo(color_by_group)

    for year in args.years:
        mr_files = get_files("fake_rate/0701", year)
        cr_files = get_files("fake_rate/0711", year)
        # files.extend(get_files(year, "fake_rate", "data"))
        # files.extend()

        # sideband(mr_files, ginfo, year)
        measurement(mr_files, ginfo, year)
        # closure(cr_files, ginfo, year)
