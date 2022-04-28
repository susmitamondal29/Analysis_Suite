#!/usr/bin/env python3
from dataclasses import dataclass
from typing import ClassVar
import warnings
import numpy as np

from analysis_suite.commons.histogram import Histogram
from analysis_suite.Plotting.stack import Stack
from analysis_suite.Variable_Creator.vargetter2 import VarGetter
from analysis_suite.commons.plot_utils import ratio_plot, setup_mplhep, plot, plot_colorbar

hep = setup_mplhep()

def setup_histogram(group, vg_dict, chan, graph_info):
    output = Histogram(group, *graph_info.bins())
    if group != "":
        output.set_plot_details(graph_info.info)

    for mem, vg in vg_dict.items():
        vals, scale = graph_info.func(vg, chan)
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

def plot_ratio1d(stack, data, plot_name, axis_name, lumi, channel=None):
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

def setup_plot(mc_vg, data_vg, chan, graph_info, filename, region, scales = None):
    print(chan, region, graph_info.name)
    mc = {group: setup_histogram(group, mc_group, chan, graph_info) for group, mc_group in mc_vg.items()}
    data = setup_histogram('data', data_vg, chan, graph_info)
    stack = make_stack(mc, scales)

    latex_chan = {"Muon": "\mu", "Electron": "e", "MM": '\mu\mu', "EM": 'e\mu', "EE": 'ee'}
    region_name = f'${region} ({latex_chan[chan]})$'
    file_name = f'{filename}_{region}_{graph_info.name}'
    axis_name = graph_info.axis_name.format(latex_chan[chan])
    plot_ratio1d(stack, data, file_name, axis_name, graph_info.lumi, region_name)

def get_fake_rate(part, fake_rate, idx):
    pt_axis, eta_axis = fake_rate.axes
    npt, neta = fake_rate.axes.size

    ptbin = np.digitize(part['pt', idx], pt_axis.edges) - 1
    ptbin = np.where(ptbin == npt, npt-1, ptbin)
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

    def bins(self):
        if isinstance(self.bin_tuple, tuple):
            return self.bin_tuple
        else:
            return (self.bin_tuple,)
