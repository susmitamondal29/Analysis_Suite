#!/usr/bin/env python3
import uproot
import numpy as np
from dataclasses import dataclass
import awkward as ak
from typing import ClassVar
from sklearn.metrics import roc_curve
from scipy.stats import kurtosis
from copy import copy
from prettytable import PrettyTable

from analysis_suite.Variable_Creator.vargetter import VarGetter
from analysis_suite.commons.histogram import Histogram
from analysis_suite.commons.constants import lumi
import analysis_suite.commons.configs as config
from analysis_suite.commons.info import fileInfo
from analysis_suite.commons.plot_utils import plot, nonratio_plot, ratio_plot, hep

from .stack import Stack

@dataclass
class GraphInfo:
    name: str = ""
    axis_name: str = ""
    bin_tuple: object = None
    func: object = None
    output: str = 'stack'
    info: ClassVar[object] = None
    cuts: object = None

    def bins(self):
        if isinstance(self.bin_tuple, tuple):
            return self.bin_tuple
        else:
            return (self.bin_tuple,)



class Plotter:
    fom_label = {'likely': '\sqrt{-2\ln{\lambda(0)}}',
                 's/sqrtb': 'S/\sqrt{B}'}
    sig_colors = ['Signal', '#ef8a62'] #     '#f1a340' '#7fbf7b' '#d8b365' '#ef8a62'
    bkg_colors = ['Background', "#67a9cf"] # '#998ec3' '#af8dc3' '#5ab4ac' "#67a9cf"

    def __init__(self, filename, groups, ntuple=None, cuts=None, year="2016", **kwargs):
        self.dfs = dict()
        self.sig = ""
        self.bkg = []
        self.groups = copy(groups)
        self.readtype = 'flat'
        self.graphs = dict()
        self.lumi = lumi[year]

        if ntuple is None:
            self.setup_flat(filename, cuts)
        else:
            self.readtype = 'ntuple'
            self.setup_ntuple(filename, ntuple, **kwargs)
        self.clean_groups(groups)


    def set_groups(self, sig, bkg=None):
        self.sig = sig
        self.bkg = bkg


    def clean_groups(self, groups):
        for group, members in groups.items():
            new_members = [member for member in members if member in self.dfs]
            self.groups[group] = new_members
        

    def get_hists(self, name, group=None):
        if group is None:
            return self.hists[name]
        else:
            return self.hists[name][group]


    def setup_ntuple(self, filenames, ntuple, systName="Nominal"):
        root_files = filenames.glob("*.root") if filenames.is_dir() else [filenames]
        for root_file in root_files:
            members = config.get_dirnames(root_file)
            syst = config.get_syst_index(root_file, systName)
            if syst == -1:
                continue
            for member in members:
                xsec = fileInfo.get_xsec(member)*self.lumi*1000 if member != 'data' else 1
                for tree in ntuple.trees:
                    if "Signal" in tree and member == "data":
                        continue # blind SR
                    vg = VarGetter(root_file, tree, member, xsec, syst)
                    if (new_name := ntuple.get_change(tree, member)):
                        member = new_name
                    if not vg:
                        continue
                    if member not in self.dfs:
                        self.dfs[member] = dict()
                    ntuple.apply_cut(vg)
                    vg.setSyst(systName)
                    vg.mergeParticles("TightLepton", "TightMuon", "TightElectron")
                    self.dfs[member][tree] = vg


    def setup_flat(self, filename, cuts):
        remove = list()
        with uproot.open(filename) as f:
            for group, members in self.groups.items():
                for member in members:
                    if member not in f:
                        continue
                    self.dfs[member] = self.apply_cut(f[member].arrays(), cuts)


    def fill_hists(self, graphs, ginfo=None, subset=None):
        if isinstance(graphs, dict):
            self.graphs = graphs
        elif isinstance(graphs, list):
            self.graphs = {graph.name: graph for graph in graphs}
        else:
            self.graphs = {graphs.name: graphs}
        self.hists = {name: dict() for name in self.graphs.keys() }
        for group, members in self.groups.items():
            for name, graph in self.graphs.items():
                self.hists[name][group] = Histogram(group, *graph.bins())
                for member in members:
                    if subset is not None and name not in subset:
                        continue
                    vals, weight = self.get_array(member, graph)
                    self.hists[name][group].fill(vals, weight=weight, member=member)

            if ginfo is not None:
                self.hists[name][group].set_plot_details(ginfo)


    def get_array(self, member, graph):
        if self.readtype == 'flat':
            df = self.apply_cut(self.dfs[member], graph.cuts)
            return np.nan_to_num(df[graph.func], nan=-1000), df['scale_factor']
        elif self.readtype == 'ntuple':
            vals, scales = np.array([[],[]])
            for tree, vg in self.dfs[member].items():
                v, s = graph.func(vg)
                vals = np.concatenate((vals, v))
                scales = np.concatenate((scales, s))
            return vals, scales


    def apply_cut(self, df, cut):
        if cut is None:
            return df
        elif isinstance(cut, list):
            for cut_ in cut:
                df = apply_cut(df, cut_)
            return df
        else:
            if len(cutter := cut.split("<")) > 1:
                return df[df[cutter[0]] < float(cutter[1])]
            elif len(cutter := cut.split(">")) > 1:
                return df[df[cutter[0]] > float(cutter[1])]
            elif len(cutter := cut.split("==")) > 1:
                return df[df[cutter[0]] == float(cutter[1])]
            else:
                raise Exception(f'{cut} is not formatted correctly')


    def get_fom(self, graph, bins, sig_type="likely"):
        s_tot = np.zeros(len(bins))
        b_tot = np.zeros(len(bins))
        for group, members in self.groups.items():
            for member in members:
                values, scales = self.get_array(member, graph)
                if group in self.sig:
                    b_tot += np.array([np.sum(scales[values > val]) for val in bins])
                elif group in self.bkg:
                    s_tot += np.array([np.sum(scales[values > val]) for val in bins])
        if sig_type == "likely":
            return config.likelihood_sig(s_tot, b_tot)
        elif sig_type == "s/sqrtb":
            return config.asymptotic_sig(s_tot, b_tot)
        else:
            raise AttributeError(f"Significance type {sig_type} not allowed!")

    def plot_from_graph(self, graph, outfile, **kwargs):
        if graph.output == "fom":
            self.plot_fom(graph.name, outfile)
        elif graph.output == "shape":
            self.plot_shape(graph.name, outfile)
        elif graph.output == 'roc':
            self.plot_roc(outfile)
        elif graph.output == 'stack':
            self.plot_stack(graph.name, outfile, **kwargs)
        else:
            raise AttributeError(f"Not correct Output type: graph.output=={graph.output}")
        

    def plot_fom(self, name, outfile, bins=None, sig_type='likely'):
        graph = self.graphs[name]
        if bins is None:
            bins = graph.bin_tuple.edges
        discrete = np.all(np.unique(np.diff(bins)) == 1)

        with plot(outfile) as ax:
            sig = self.get_sum(self.sig, graph, self.sig_colors)
            bkg = self.get_sum(self.bkg, graph, self.bkg_colors)
            sig.plot_shape(ax)
            bkg.plot_shape(ax)
            ax.set_ylabel("Normalized Events (A.U)")
            ax.set_xlabel(graph.axis_name, horizontalalignment='right', x=1.0)

            # Plot FOM details
            ax2 = ax.twinx()
            fom = self.get_fom(graph, bins, sig_type)
            maxbin = bins[np.argmax(fom)]
            full_label = f'${self.fom_label[sig_type]}={max(fom):.3f}$\n cut={maxbin:.2f}'
            if discrete:
                ax2.hist(bins=bins, x=bins, weights=fom, label=full_label, histtype='step', edgecolor='k')
            else:
                ax2.plot(bins, fom, label=full_label, color = 'k')
            ax2.plot(np.linspace(bins[0], bins[-1], 5), [max(fom)]*5, linestyle=':', color='k')
            ax2.set_ylabel("FOM", horizontalalignment='right', y=1.0)

            # Make Legend
            lines, labels = ax2.get_legend_handles_labels()
            lines2, labels2 = ax.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2)

        return (fom, maxbin)


    def plot_shape(self, name, outfile):
        graph = self.graphs[name]
        with nonratio_plot(outfile, graph.axis_name, graph.bin_tuple.edges) as ax:
            sig = self.get_sum(self.sig, graph, self.sig_colors)
            bkg = self.get_sum(self.bkg, graph, self.bkg_colors)
            sig.plot_shape(ax)
            bkg.plot_shape(ax)
            ax.set_ylabel("Normalized Events (A.U)")


    # def plot_roc(self, outfile):
    #     with nonratio_plot(outfile/'roc.png', "False Positive Rate", [0., 1.]) as ax:
    #         pred, truth, weight = np.array([]), np.array([]), np.array([])
    #         for group, df in self.dfs.items():
    #             if group in self.sig:
    #                 truth = np.append(truth, np.ones(len(df)))
    #             else:
    #                 truth = np.append(truth, np.zeros(len(df)))
    #             weight = np.append(weight, df['scale_factor'])
    #             pred = np.append(pred, df['Signal'])
    #         fpr, tpr, _ = roc_curve(truth, pred, sample_weight=weight)
    #         auc = np.trapz(tpr, fpr)

    #         ax.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
    #         ax.plot(np.linspace(0, 1, 5), np.linspace(0, 1, 5), linestyle=':')
    #         ax.set_ylabel("True Positive Rate", horizontalalignment='right', y=1.0)


    def plot_stack(self, name, outfile, **kwargs):
        graph = self.graphs[name]
        signal = self.hists[graph.name][self.sig]
        stack = self.make_stack(name)
        data = False

        with ratio_plot(outfile, graph.axis_name, stack.get_xrange(), **kwargs) as ax:
            ratio = Histogram("Ratio", graph.bin_tuple, color="black")
            band = Histogram("Ratio", graph.bin_tuple, color="plum")
            error = Histogram("Stat Errors", graph.bin_tuple, color="plum")

            ratio += signal/stack
            band += stack/stack
            for hist in stack.stack:
                error += hist

            pad, subpad = ax

            #upper pad
            stack.plot_stack(pad)
            signal.plot_points(pad)
            error.plot_band(pad)

            # ratio pad
            ratio.plot_points(subpad)
            band.plot_band(subpad)

            hep.cms.label(ax=pad, lumi=self.lumi, data=data)


    def get_sum(self, groups, graph, details=None):
        all_hist = Histogram("", *graph.bins())
        if isinstance(groups, str):
            all_hist += self.hists[graph.name][groups]
        else:
            for group in groups:
                if group not in self.hists[graph.name]:
                    continue
                all_hist += self.hists[graph.name][group]
        if details is not None:
            all_hist.set_plot_details(details)
        return all_hist


    def print_info(self, varname):
        info = list()
        graph = self.graphs[varname]
        for group, members in self.groups.items():
            for member in members:
                vals, weight = self.get_array(member, graph)
                info.append({
                    "name" : member,
                    "group" : group,
                    "mean": np.mean(vals),
                    "std":  np.std(vals),
                    "kurtosis": kurtosis(vals),
                    'nRaw': len(vals),
                    'nEvents': np.sum(weight)
                })

        table = PrettyTable(["Name", "Group", "Events", "Raw", "Mean", "Kurtosis"])
        info = sorted(info, reverse=True, key=lambda x: x["mean"])

        for arr in info:
            table.add_row([arr['name'], arr['group'], config.sig_fig(arr['nEvents']), arr['nRaw'],
                          f'{arr["mean"]:.2f}+-{arr["std"]:.2f}', config.sig_fig(arr['kurtosis'])])
        print(table.get_string())


    def make_stack(self, name):
        stack = Stack(*self.graphs[name].bins())
        for group in self.bkg:
            stack += self.hists[name][group]
        return stack



# for key, hist in file["shapes_fit_s/yr2018"].items():
#     key = key[:key.index(";")]
#     # Need to deal with Data
#     if "data" in key:
#         x, y = hist.member("fX"), hist.member("fY")
#         data += data.fill(x, weight=y)
#     if "TH1" not in repr(hist):
#         continue
#     hist = hist.to_boost()
#     if "total" in key:
#         continue
#     elif key == signalName:
#         signal += hist


#     groupHist = Histogram(key, hist.axes[0])
#     groupHist.set_plot_details(group_info)
#     groupHist += hist
#     stacker += groupHist
