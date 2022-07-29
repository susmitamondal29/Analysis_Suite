#!/usr/bin/env python3
from dataclasses import dataclass
from typing import ClassVar
import warnings
import numpy as np
import uproot

from analysis_suite.commons.histogram import Histogram
from analysis_suite.Plotting.stack import Stack
from analysis_suite.commons.info import fileInfo
from analysis_suite.Variable_Creator.vargetter import VarGetter
from analysis_suite.commons.plot_utils import ratio_plot, setup_mplhep, plot, plot_colorbar

hep = setup_mplhep()

def setup_histogram(group, vg_dict, chan, graph_info):
    output = Histogram(group, *graph_info.bins())
    if group != "":
        output.set_plot_details(graph_info.info)

    for mem, vg in vg_dict.items():
        vals, scale = graph_info.func(vg, chan)
        # print(mem, chan, sum(scale), len(scale))
        lumi = graph_info.lumi*1000 if mem != 'data' else 1
        if isinstance(vals, tuple):
            output.fill(*vals, weight=lumi*scale, member=mem)
        else:
            output.fill(vals, weight=lumi*scale, member=mem)
    return output


def setup_events(dataInfo, branch, syst = 0):
    output = dict()
    for group, member_info in dataInfo.members.items():
        print(group)
        output[group] = dict()
        for member, xsec in member_info.items():
            vg = VarGetter(dataInfo.filename, branch, member, xsec, syst)
            if not len(vg):
                continue
            print(member, sum(vg.scale), len(vg.scale))
            output[group][member] = vg
    return output

def make_stack(hist_dict, scales=None):
    stack = Stack(*list(hist_dict.values())[0].axes)
    for group, hist in hist_dict.items():
        if scales is not None and group in scales:
            hist.scale(scales[group], changeName=True)
        stack += hist
    return stack

def mask_vg(vgs, mask_func):
    for vg in vgs.values():
        if isinstance(vg, VarGetter):
            vg.clear_mask()
            vg.mask = mask_func(vg)
        else:
            mask_vg(vg, mask_func)

def plot_ratio1d(stack, data, plot_name, axis_name, lumi, channel=None, ylim=None):
    with ratio_plot(plot_name, axis_name, stack.get_xrange()) as ax:
        ratio = Histogram("Ratio", data.axis, color="black")
        band = Histogram("Ratio", data.axis, color="plum")
        error = Histogram("Stat Errors", data.axis, color="plum")

        ratio += data/stack
        band += stack/stack
        for hist in stack.stack:
            error += hist

        pad, subpad = ax

        #upper pad
        stack.plot_stack(pad)
        data.plot_points(pad)
        error.plot_band(pad)

        # ratio pad
        ratio.plot_points(subpad)
        band.plot_band(subpad)
        if channel is not None:
            subpad.text(data.axis.edges[0], -0.7, channel)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hep.cms.label(ax=pad, lumi=lumi, data=data)

        if ylim is not None:
            pad.set_ylim(top=ylim)

def setup_plot(mc_vg, data_vg, chan, graph_info, filename, region, scales = None, ylim=None):
    print(chan, region, graph_info.name)
    mc = {group: setup_histogram(group, mc_group, chan, graph_info) for group, mc_group in mc_vg.items()}
    data = setup_histogram('data', data_vg, chan, graph_info)
    stack = make_stack(mc, scales)

    latex_chan = {"Muon": "\mu", "Electron": "e", "MM": '\mu\mu', "EM": 'e\mu', "EE": 'ee'}
    region_name = f'${region} ({latex_chan[chan]})$'
    file_name = f'{filename}_{region}_{graph_info.name}'
    axis_name = graph_info.axis_name.format(latex_chan[chan])
    plot_ratio1d(stack, data, file_name, axis_name, graph_info.lumi, region_name, ylim)

def get_fake_rate(part, fake_rate, idx):
    pt_axis, eta_axis = fake_rate.axes
    npt, neta = fake_rate.axes.size

    ptbin = np.digitize(part['pt', idx], pt_axis.edges) - 1
    ptbin = np.where(ptbin >= npt, npt-1, ptbin)
    etabin = np.digitize(part.abseta(idx), eta_axis.edges) - 1
    return fake_rate.values().flatten()[etabin + neta*ptbin]



@dataclass
class DataInfo:
    filename: str
    year: str
    members : dict = None

    def __post_init__(self):
        self.members = {}

    def setup_member(self, info, finfo, group):
        self.members[group] = {mem: finfo.get_xsec(mem) for mem in info.get_members(group)}

@dataclass
class GraphInfo:
    name: str
    axis_name: str
    bin_tuple: object
    func: object
    info: ClassVar[object] = None
    lumi: ClassVar[float] = None
    cuts: object = None

    def bins(self):
        if isinstance(self.bin_tuple, tuple):
            return self.bin_tuple
        else:
            return (self.bin_tuple,)



#####################################
# NEW STUFF
#####################################



def fill_histograms(files, mask_funcs, graphs, groups, chans, branch, lumi, scaler=None, syst=0):
    out_hists = dict()
    for graph in graphs:
        out_hists[graph.name] = dict()
        for chan in chans:
            out_hists[graph.name][chan] = {group: Histogram(group, *graph.bins()) for group in groups.keys()}

    total_files = len(files)
    for i, filename in enumerate(files):
        members = get_dirnames(filename)
        for member in members:
            group = get_by_val(groups, member)
            if group is None:
                continue
            xsec = fileInfo.get_xsec(member)

            vg = VarGetter(filename, branch, member, xsec, syst)
            print(member, len(vg.scale), lumi*sum(vg.scale) if member != 'data' else sum(vg.scale))
            if isinstance(scaler, list):
                for sc in scaler:
                    sc(vg)
            elif scaler is not None:
                scaler(vg)
            for chan in chans:
                vg.clear_mask()
                vg.mask = mask_funcs[chan](vg)
                for graph in graphs:
                    vals, scale = graph.func(vg, chan)
                    if group != "data":
                        scale *= lumi
                    if isinstance(vals, tuple):
                        out_hists[graph.name][chan][group].fill(*vals, weight=scale, member=member)
                    else:
                        out_hists[graph.name][chan][group].fill(vals, weight=scale, member=member)
            vg.close()
    return out_hists



def get_by_val(dic, val):
    for key, list_ in dic.items():
         if val in list_:
             return key
    return None


def setup_groups(groups, ginfo):
    group_dict = dict()
    for group in groups:
        group_dict[group] = [mem for mem in ginfo.get_members(group)]
    return group_dict

def make_plot(hist_dict, graph_info, chan, lumi, filename, region, data_name='data'):
    data = hist_dict[data_name]
    data.color = 'k'
    stack = make_stack({key: hist for key, hist in hist_dict.items() if key != data_name})
    latex_chan = {"Muon": "\mu", "Electron": "e", "MM": '\mu\mu', "EM": 'e\mu', "EE": 'ee'}
    region_name = f'${region} ({latex_chan[chan]})$'
    file_name = f'{filename}_{region}_{graph_info.name}'
    axis_name = graph_info.axis_name.format(latex_chan[chan])
    plot_ratio1d(stack, data, file_name, axis_name, lumi, region_name)

def set_plot_details(hists, ginfo):
    for hist in hists.values():
        if isinstance(hist, Histogram):
            hist.set_plot_details(ginfo)
        else:
            set_plot_details(hist, ginfo)

def plot_project(filename, tight, loose, axis, axis_label, lumi):
    with plot(filename) as ax:
        eff_hist = Histogram.efficiency(tight.project(axis), loose.project(axis))
        eff_hist.plot_points(ax)
        ax.set_xlabel(axis_label)
        hep.cms.label(ax=ax, lumi=lumi)

def add_histgroups(reciever, base, groups):
    if isinstance(groups, str):
        groups = [groups]
    for graph, graph_hists in base.items():
        for chan, chan_hists in graph_hists.items():
            for group in groups:
                reciever[graph][chan][group] = chan_hists[group]
