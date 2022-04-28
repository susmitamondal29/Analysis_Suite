#!/usr/bin/env python3
import boost_histogram as bh
import argparse
from scipy.optimize import minimize
import numpy as np
import pickle
from pathlib import Path

from analysis_suite.commons.histogram import Histogram
from analysis_suite.commons.plot_utils import plot, plot_colorbar
from analysis_suite.commons.info import FileInfo, GroupInfo, PlotInfo
from fake_rate_helper import setup_events, setup_histogram, setup_plot, mask_vg, DataInfo, GraphInfo, hep

trig_scale = {
    "2016": {
        "Electron" : [0.8670, 1.0125],
        "Muon" : [0.7023, 0.9768],
    },
    "2017": {
        "Electron" : [0.9540, 1.1406],
        "Muon" : [0.7123, 1.0358],
    },
    "2018": {
        "Electron" : [0.9491, 1.1130],
        "Muon" : [0.9074, 1.1205],
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

def scale_trigger(vg, chan, trig_scale):
    pt = np.where(vg[f'Fake{chan}'].num() == 1, vg[f"Fake{chan}"].pad('pt', 0), vg[f"Tight{chan}"].pad('pt', 0))
    lowpt_weight = (pt > 10)*(pt < 25)*trig_scale[0]
    highpt_weight = (pt > 25)*trig_scale[1]
    vg.scale = (lowpt_weight+highpt_weight)*vg.scale

def scale_fake(vg, chan, fakerate):
    mask = vg[f'Fake{chan}'].num() > 0
    scales = list()
    for pt, eta in zip(vg[f'Fake{chan}']['pt', 0], vg[f'Fake{chan}'].abseta(0)):
        pt = min(pt, 89)
        scales.append(fakerate[bh.loc(pt), bh.loc(eta)].value)
    scale = np.array(scales)
    vg.scale[mask] = (scale)/(1-scale)*vg.scale[mask]


def fr_plot(name, tight, loose, **kwargs):
    with plot(name) as ax:
        mesh = (tight/loose).plot_2d(ax, **kwargs)
        ax.set_xlabel("$p_{T}(\mu)$ [GeV]")
        ax.set_ylabel("$|\eta(\mu)|$")
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


def np_sideband(year, lumi, ginfo, finfo, args):
    Path(f'SB_{year}').mkdir(exist_ok=True)

    pt_tight = GraphInfo("tightpt", '$p_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_tight(vg, chan, "pt"))
    mt_tight = GraphInfo("tightmt", '$M_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_tight(vg, chan, 'mt'))
    met = GraphInfo("met", '$MET$', bh.axis.Regular(20, 30, 200), lambda vg, chan : vg.get_hist("Met"))
    met_phi = GraphInfo("metphi", '$\phi(MET)$', bh.axis.Regular(20, -np.pi, np.pi), lambda vg, chan : vg.get_hist("Met_phi"))

    data_info = DataInfo(Path(f"fake_rate_data_{year}.root"), year)
    data_info.setup_member(ginfo, finfo, "data")

    mc_info = DataInfo(Path(f"fake_rate_mc_{year}.root"), year)
    mc_info.setup_member(ginfo, finfo, "ewk")
    mc_info.setup_member(ginfo, finfo, "qcd")

    side_data = setup_events(data_info, "SideBand")['data']
    side_mc = setup_events(mc_info, "SideBand")

    mc_scale_factors = dict()

    for chan in args.sb_chan:
        name = f'SB_{year}/{chan}_{year}'

        # Masking
        chan_mask = lambda vg : (vg[f'Tight{chan}'].num() == 1)
        mask_vg(side_mc, chan_mask)
        mask_vg(side_data, chan_mask)

        for graph in [pt_tight, mt_tight, met, met_phi]:
            setup_plot(side_mc, side_data, chan, graph, name+"_notrig", "SB")
        scale_trigger(side_data['data'], chan, trig_scale[year][chan])
        for graph in [pt_tight, mt_tight, met, met_phi]:
            setup_plot(side_mc, side_data, chan, graph, name, 'SB')

        # Fitting
        mc_mt_sb = {group: setup_histogram(group, side_vgs, chan, mt_tight) for group, side_vgs in side_mc.items()}
        data_mt_sb = setup_histogram('data', side_data, chan, mt_tight)
        qcd_f, ewk_f = fit_template(data_mt_sb, mc_mt_sb['qcd'], mc_mt_sb["ewk"])
        qcd_ml_f, ewk_ml_f = fit_template(data_mt_sb, mc_mt_sb['qcd'], mc_mt_sb["ewk"], fit_type='ml')

        print(qcd_f, ewk_f)
        print(qcd_ml_f, ewk_ml_f)

        mc_scale_factors[chan] = {"ewk": ewk_f, 'qcd': qcd_f}
        for graph in [pt_tight, mt_tight, met, met_phi]:
            setup_plot(side_mc, side_data, chan, graph, f'{name}_SB_scaled', region="SB", scales=mc_scale_factors[chan])

    # Dump MC scale factors
    with open(f"mc_scales_{year}.pickle", "wb") as f:
        pickle.dump(mc_scale_factors, f)


def np_fake_rate(year, lumi, ginfo, finfo, args):
    Path(f'MR_{year}').mkdir(exist_ok=True)

    ptbins = bh.axis.Variable([15, 20, 25, 35, 50, 70, 90])
    etabins = bh.axis.Variable([0.0, 1.2, 2.1, 2.4])

    pt_loose = GraphInfo("loosept", '$p_{{T}}({}_{{loose}})$', bh.axis.Regular(20, 0, 150), lambda vg, chan : get_all(vg, chan, 'pt'))
    pt_tight = GraphInfo("tightpt", '$p_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 200), lambda vg, chan : get_tight(vg, chan, "pt"))
    mt_loose = GraphInfo("loosemt", '$M_{{T}}({}_{{loose}})$', bh.axis.Regular(20, 0, 20), lambda vg, chan : get_all(vg, chan, 'mt'))
    mt_tight = GraphInfo("tightmt", '$M_{{T}}({}_{{tight}})$', bh.axis.Regular(20, 0, 20), lambda vg, chan : get_tight(vg, chan, 'mt'))
    met = GraphInfo("met", '$MET$', bh.axis.Regular(20, 0, 30), lambda vg, chan : vg.get_hist("Met"))
    met_phi = GraphInfo("metphi", '$\phi(MET)$', bh.axis.Regular(20, -np.pi, np.pi), lambda vg, chan : vg.get_hist("Met_phi"))
    pt_eta_all = GraphInfo("loosefr", '', (ptbins, etabins), lambda vg, chan : get_all_pteta(vg, chan))
    pt_eta_tight = GraphInfo("tightfr", '', (ptbins, etabins), lambda vg, chan : vg[f"Tight{chan}"].get_hist2d('pt', 'abseta', 0))

    data_info = DataInfo(Path(f"fake_rate_data_{year}.root"), year)
    data_info.setup_member(ginfo, finfo, "data")

    mc_info = DataInfo(Path(f"fake_rate_mc_{year}.root"), year)
    mc_info.setup_member(ginfo, finfo, "ewk")
    mc_info.setup_member(ginfo, finfo, "qcd")

    measure_data = setup_events(data_info, "Measurement")['data']
    measure_mc = setup_events(mc_info, "Measurement")

    fake_rates = dict()

    # Load MC scale factors
    with open(f"mc_scales_{year}.pickle", "rb") as f:
        mc_scale_factors = pickle.load(f)

    for chan in args.fr_chan:
        name = f'MR_{year}/{chan}_{year}'
        fake_rates[chan] = dict()

        # Masking
        chan_mask = lambda vg : (vg[f'Tight{chan}'].num() == 1)+(vg[f'Fake{chan}'].num() == 1)
        mask_vg(measure_mc, chan_mask)
        mask_vg(measure_data, chan_mask)

        for graph in [pt_loose, pt_tight, mt_loose, mt_tight, met, met_phi]:
            setup_plot(measure_mc, measure_data, chan, graph, name+"_notrig", "MR")
        scale_trigger(measure_data['data'], chan, trig_scale[year][chan])
        for graph in [pt_loose, pt_tight, mt_loose, mt_tight, met, met_phi]:
            setup_plot(measure_mc, measure_data, chan, graph, name, "MR")

        for graph in [pt_loose, pt_tight, mt_loose, mt_tight, met, met_phi]:
            setup_plot(measure_mc, measure_data, chan, graph, name+'_scaled', 'MR', scales=mc_scale_factors[chan])

        # Calculate Fake Rate
        qcd_f, ewk_f = mc_scale_factors[chan].values()
        mc_tight_pteta = {group: setup_histogram(group, measure_vgs, chan, pt_eta_tight) for group, measure_vgs in measure_mc.items()}
        data_tight_pteta = setup_histogram('data', measure_data, chan, pt_eta_tight)
        data_corr_tight_pteta = data_tight_pteta - ewk_f*mc_tight_pteta["ewk"]

        mc_all_pteta = {group: setup_histogram(group, measure_vgs, chan, pt_eta_all) for group, measure_vgs in measure_mc.items()}
        data_all_pteta = setup_histogram('data', measure_data, chan, pt_eta_all)
        data_corr_all_pteta = data_all_pteta - ewk_f*mc_all_pteta["ewk"]

        fake_rates[chan]["qcd"] = Histogram.efficiency(mc_tight_pteta['qcd'], mc_all_pteta['qcd']).hist
        fake_rates[chan]["data"] = Histogram.efficiency(data_tight_pteta, data_all_pteta).hist
        fake_rates[chan]["data_ewk"] = Histogram.efficiency(data_corr_tight_pteta, data_corr_all_pteta).hist

        # Fake Rate Plotting
        fr_plot(f"{name}_fr_data", data_tight_pteta, data_all_pteta)
        fr_plot(f"{name}_fr_qcd", mc_tight_pteta['qcd'], mc_all_pteta['qcd'])
        fr_plot(f"{name}_fr_ewkcorr", data_corr_tight_pteta, data_corr_all_pteta)

        with plot(f'{name}_fr_pt_{year}') as ax:
            fr_pt = Histogram.efficiency(data_corr_tight_pteta.project(0), data_corr_all_pteta.project(0))
            fr_pt.plot_points(ax)
            hep.cms.label(ax=ax, lumi=lumi)

        with plot(f'{name}_fr_eta_{year}') as ax:
            fr_eta = Histogram.efficiency(data_corr_tight_pteta.project(1), data_corr_all_pteta.project(1))
            fr_eta.plot_points(ax)
            hep.cms.label(ax=ax, lumi=lumi)

    # Dump Fake rates
    with open(f"fr_{year}.pickle", "wb") as f:
        pickle.dump(fake_rates, f)



def np_closure(year, lumi, ginfo, finfo, args):
    Path(f'CR_{year}').mkdir(exist_ok=True)

    met = GraphInfo("met", '$MET$', bh.axis.Regular(20, 0, 200), lambda vg, chan : vg.get_hist("Met"))
    ht = GraphInfo("ht", '$H_T$', bh.axis.Regular(15, 0, 600), lambda vg, chan : vg.get_hist("HT"))
    njet = GraphInfo("njets", '$N_j$', bh.axis.Regular(8, 0, 8), lambda vg, chan : (vg.Jets.num(), vg.scale))
    nbjet = GraphInfo("nbjets", '$N_b$', bh.axis.Regular(8, 0, 8), lambda vg, chan : (vg.BJets.num(), vg.scale))
    nloosebjet = GraphInfo("nloosebjets", '$N_{{bloose}}$', bh.axis.Regular(8, 0, 8), lambda vg, chan : vg.get_hist("N_bloose"))
    ntightbjet = GraphInfo("ntightbjets", '$N_{{btight}}$', bh.axis.Regular(8, 0, 8), lambda vg, chan : vg.get_hist("N_btight"))

    data_info = DataInfo(Path(f"data_closure_{year}.root"), year)
    data_info.setup_member(ginfo, finfo, "data")

    mc_info = DataInfo(Path(f"mc_closure_{year}.root"), year)
    mc_info.setup_member(ginfo, finfo, "ttbar_lep")
    mc_info.setup_member(ginfo, finfo, "wjet_ht")

    data_tf = setup_events(data_info, "Closure_TF")['data']
    mc_tf = setup_events(mc_info, "Closure_TF")
    mc_tt = setup_events(mc_info, "Closure_TT")

    tt_masks = {"MM": lambda vg: vg.TightMuon.num() == 2,
                "EE": lambda vg: vg.TightElectron.num() == 2,
                "EM": lambda vg: num_two_parts(vg.TightMuon, vg.TightElectron),
                }
    tf_masks = {"MM": lambda vg: num_two_parts(vg.TightMuon, vg.FakeMuon),
                "EE": lambda vg: num_two_parts(vg.TightElectron, vg.FakeElectron),
                "EM": lambda vg: num_two_parts(vg.TightMuon, vg.FakeElectron)+num_two_parts(vg.TightElectron, vg.FakeMuon)
                }

    # TF control region
    for chan in args.close_chan:
        mask_vg(mc_tf, tf_masks[chan])
        mask_vg(data_tf, tf_masks[chan])

        name = f'CR_{year}/{chan}_{year}'

        for graph in [met, ht, njet, nbjet, nloosebjet, ntightbjet]:
            setup_plot(mc_tf, data_tf, chan, graph, name, "TF")

    data_tf['data'].clear_mask()
    with open(f"fr_{year}.pickle", "rb") as f:
        fake_rates = pickle.load(f)
    scale_fake(data_tf['data'], "Muon", fake_rates["Muon"]['qcd'])
    scale_fake(data_tf['data'], "Electron", fake_rates['Electron']['qcd'])
    nonprompt = {"nonprompt", data_tf}

    for chan in args.close_chan:
        mask_vg(mc_tt, tt_masks[chan])
        mask_vg(data_tf, tf_masks[chan])

        name = f'CR_{year}/{chan}_{year}'

        for graph in [met, ht, njet, nbjet, nloosebjet, ntightbjet]:
            setup_plot(mc_tt, data_tf, chan, graph, name, "TT")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--years", required=True,
                        type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                                   else [i.strip() for i in x.split(',')],
                        help="Year to use")
    parser.add_argument("--fr_chan", default='all',
                        type=lambda x: ['Electron', 'Muon'] if x == 'all' \
                                   else [i.strip() for i in x.split(',')],
                        help="Channels for the fake")
    parser.add_argument("--sb_chan", default='all',
                        type=lambda x: ['Electron', 'Muon'] if x == 'all' \
                                   else [i.strip() for i in x.split(',')],
                        help="Channels for the fake")

    parser.add_argument("--close_chan", default='all',
                        type=lambda x: ['MM', 'EE', 'EM'] if x == 'all' \
                                   else [i.strip() for i in x.split(',')],
                        help="Channels for the Closure")


    args = parser.parse_args()

    color_by_group = {
        "data": "black",
        "qcd": "grey",
        "ewk": "orange",
        "wjet_ht": "olive",
        "ttbar_lep": "royalblue",
        'nonprompt': 'lightgrey'
    }
    ginfo = GroupInfo(color_by_group)
    GraphInfo.info = ginfo

    for year in args.years:
        lumi = PlotInfo.lumi[year]
        GraphInfo.lumi = lumi
        finfo = FileInfo(year)

        np_sideband(year, lumi, ginfo, finfo, args)
        np_fake_rate(year, lumi, ginfo, finfo, args)
        np_closure(year, lumi, ginfo, finfo, args)
