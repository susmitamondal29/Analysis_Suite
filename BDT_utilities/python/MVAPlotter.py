"""
.. module:: MVAPlotter
   :synopsis: Takes MvaMaker output and creates graphs
.. moduleauthor:: Dylan Teague
"""
import sys
from os.path import isfile
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as clr
from sklearn.metrics import roc_curve, roc_auc_score
import xgboost as xgb
import uproot4 as uproot
import operator

from contextlib import contextmanager

from analysis_suite.commons.info import PlotInfo
# import shap

@contextmanager
def plot(filename, option=""):
    fig, ax = plt.subplots()
    yield ax
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)


class MVAPlotter(object):
    """Wrapper for a bunch of plotting and outputing functions

    Args:
      groups(list): List of group names
      do_show(bool): Bool for if matplotlib should show its graphs
      save_dir(string): Directory name to save all plots
      lumi(float): Luminosity (in ipb)
      color_dict(dict: dict): Dictionary for setting line color for groups
      work_set(pandas.DataFrame): DataFrame with event/variable data
    """
    def __init__(self, groupDict, filetype, syst, workdir, years, **kwargs):
        self.group_dict = groupDict
        self.group_dict["NotTrained"] = list()
        self.years = years
        self.data = dict()
        self.workdir = workdir
        self.fType = filetype

        for year in years:
            trainSamples = set(sum(self.group_dict.values(), []))
            with uproot.open(workdir / year /  f'{filetype}_{syst}.root') as f:
                allSet = set([name[:name.index(";")] for name in f.keys()])
                self.data[year] = {sample.strip(";1"): data.arrays(library="pd")
                                   for sample, data in f.items()}
                for sample in allSet - trainSamples:
                    self.group_dict["NotTrained"].append(sample)

        colors = ['#f15854', '#5da5da', '#60bd68', '#faa43a', ]
        #  ['#CC0000', '#99FF00', '#FFCC00', '#3333FF']
        #  ['#462066', '#FFB85F', '#FF7A5A', '#00AAA0']

        self.color_dict = {grp: col for grp, col in zip(self.group_dict.keys(), colors)}

        # for sample, data in self.data["2016"].items():
        #     scale = self.get_scale("2016", sample)

        #     print(f'{sample} with total {sum(scale)} and error {np.sqrt(np.sum(scale**2))/np.sum(scale)}')

        # exit()



    def _darkenColor(self, color):
        cvec = clr.to_rgb(color)
        dark = 0.3
        return [i - dark if i > dark else 0.0 for i in cvec]


    def get_fom(self, var, bins, year, comb_bkg=True):
        """**Return FoM histogram**

        Args:
          sig(string): Primary group to be plotted
          bkg(string): Other groups to be plotted against sig
          var(string): Variable used to calculate Figure of Merit
          bins(numpy.ndarray): numpy array of bins
          sb_denom(bool, optional): If False, uses S/sqrt(B) instead of S/sqrt(S+B), defaults to True
          reverse(bool, optional): if True, calculates FoM using LESS than not greater than, defaults to False

        Returns:
          list: histogram of the Figure of merit (only weights)

        """
        hists = self.get_hist(var, bins, year, comb_bkg)
        cum_hists = {key: np.cumsum(vals[::-1])[::-1] for key, vals in hists.items()}
        sig = cum_hists["Signal"]
        bkg = cum_hists["Background"]
        return sig/np.sqrt(sig + bkg)

    def get_max_fom(self, var, bins, year, comb_bkg):
        return max(self.get_fom(var, bins, year, comb_bkg))

    def plot_fom(self, var, bins, year, comb_bkg=True):
        """**Plots Figure of Merits for variable scan**

        Plot figure of merit by creating a "signal region" by only
        keeping events with a value of var greater than what value is
        being scanned. One can use a cut that keeps events LESS than
        the cut for var using the reverse flag.

        Args:
          sig(string): Primary group to be plotted

        Returns:
          list: List of (FOM, bin) for the max FOM
        """
        fom_bins = np.linspace(bins[0], bins[-1], 101)
        fom = self.get_fom(var, fom_bins, year, comb_bkg)
        fom_maxbin = fom_bins[np.argmax(fom)]
        with plot(f'{self.fType}_fom_{var}_{year}.png') as ax:
            ax.plot(fom_bins[:-1], fom, label=f'$S/\sqrt{{S+B}}={max(fom):.3f}$\n cut={fom_maxbin:.2f}',
                    color = 'k')
            ax.plot(np.linspace(bins[0], bins[-1], 5), [max(fom)]*5,
                    linestyle=':', color='k')
            ax.set_xlabel("BDT value", horizontalalignment='right', x=1.0)
            ax.set_ylabel("A.U.", horizontalalignment='right', y=1.0)

            ax2 = ax.twinx()
            hists = self.get_hist(var, bins, year)
            scale = self._find_scales(hists)
            ax2.hist(x=bins[:-1], weights=hists["Signal"]*scale, bins=bins,
                    label=f'Signal x {scale}', histtype="stepfilled", linewidth=1.5,
                     density=True, alpha=0.5, color=self.color_dict["Signal"],
                     edgecolor=self._darkenColor(self.color_dict["Signal"]),
                     hatch="///")
            ax2.hist(x=bins[:-1], weights=hists["Background"], bins=bins, linewidth=1.5,
                    label=f'Background', histtype="stepfilled",
                    density=True, alpha=0.5, color=self.color_dict["Background"],
                    edgecolor=self._darkenColor(self.color_dict["Background"]),
                    hatch="///")

            lines, labels = ax2.get_legend_handles_labels()
            lines2, labels2 = ax.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc='center left')

        return (fom, fom_maxbin)

    def approx_likelihood(self, bins, year, comb_bkg=True):
        """**Get Basic max Likelihood significance**

        Args:
          bins(numpy.ndarray): numpy array of bins

        Returns:
          float: The Maximum Log Likelihood approximation (without errors)
        """
        hists = self.get_hist("Signal", bins, year, comb_bkg)
        sig, bkg = hists["Signal"], hists["Background"]

        value = (sig+bkg)*np.log(1+sig/bkg) - sig
        return math.sqrt(np.sum(2*np.nan_to_num(0.0)))


    def make_roc(self, year, comb_bkg=True):
        """Make and Save ROC curve for variable"""

        with plot(f'{self.fType}_roc_{year}.png') as ax:
            pred = self.get_var("Signal", year, comb_bkg)
            truth = self.get_classID(year, comb_bkg)
            fpr, tpr, _ = roc_curve(truth, pred)
            auc = roc_auc_score(truth, pred)

            ax.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
            ax.plot(np.linspace(0, 1, 5), np.linspace(0, 1, 5), linestyle=':')
            ax.legend()
            ax.set_xlabel("False Positive Rate", horizontalalignment='right', x=1.0)
            ax.set_ylabel("True Positive Rate", horizontalalignment='right', y=1.0)


    def apply_cut(self, cut, year):
        """**Cut DataFrame using Root Style cut string**

        Args:
          cut(string): Cut string
        """
        cutter = None
        if cut.find("<") != -1:
            cutter= (cut.split("<"), operator.lt)
        elif cut.find(">") != -1:
            cutter= (cut.split(">"), operator.gt)
        elif cut.find("==") != -1:
            cutter= (cut.split("=="), operator.eq)
        else:
            raise Exception(f'{cut} is not formatted correctly')

        opr = cutter[1]
        var, cut_val = cutter[0]
        for group, workset in self.data[year].items():
            self.data[year][group] = workset[opr(workset[var], cut_val)]


    def print_info(self, var, year):
        """**Print out basic statistics information for a variable**

        The information for each sample in a group includes the mean,
        standard deviation, kurtosis, total weighted sum, total raw
        events.

        Args:
          var(string): Variable used to print statistics
          subgroups(list): list of all the samples for the information to be printed about
        """
        from scipy.stats import kurtosis

        print("| name      | events | raw events | mean+-std | kurtosis |")
        for group, samples in self.group_dict.items():
            info = list()
            for sample in samples:
                if sample not in self.data[year]:
                    continue
                data = self.data[year][sample]
                info.append({
                    "name": sample,
                    "mean": np.mean(data[var]),
                    "std": np.std(data[var]),
                    "kurtosis": kurtosis(data[var]),
                    "nRaw": len(data[var]),
                    "nEvents": np.sum(data.scale_factor)*1000*PlotInfo.lumi[year],
                })
            info = sorted(info, reverse=True, key=lambda x: x["mean"])
            print("-"*50)
            for arr in info:
                print(f'|{arr["name"]:10} | {arr["nEvents"]:.2f}| {arr["nRaw"]} | {arr["mean"]:.2f}+-{arr["std"]:.2f} | {arr["kurtosis"]:0.2f} |')
        print("-"*50)

    def get_scale(self, year, sample):
        return self.data[year][sample].scale_factor*1000*PlotInfo.lumi[year]

    def get_var(self, var, year, comb_bkg):
        out_array = np.array([])
        for group, samples in self.group_dict.items():
            if not comb_bkg and group == "NotTrained":
                continue
            for sample in samples:
                if sample not in self.data[year]:
                    continue
                out_array = np.concatenate([out_array, self.data[year][sample][var]])
        return out_array


    def get_classID(self, year, comb_bkg):
        out_array = np.array([])
        for group, samples in self.group_dict.items():
            if not comb_bkg and group == "NotTrained":
                continue
            array = np.ones if group == "Signal" else np.zeros
            for sample in samples:
                if sample not in self.data[year]:
                    continue
                nSample = len(self.data[year][sample])
                out_array = np.concatenate([out_array, array(nSample)])
        return out_array


    def get_hist(self, var, bins, year, comb_bkg = False):
        outdata = dict()
        for group, samples in self.group_dict.items():
            outdata[group] = np.zeros(len(bins)-1)
            for sample in samples:
                if sample not in self.data[year]:
                    continue
                outdata[group] += np.histogram(self.data[year][sample][var], bins=bins, weights=self.get_scale(year, sample))[0]
        if comb_bkg:
            outdata["Background"] += outdata["NotTrained"]
            del outdata["NotTrained"]
        return outdata

    def year_shapes(self, var, bins, plot_class):
        with plot(f"{self.fType}_shape_{var}_{plot_class}.png") as ax:
            for year in self.years:
                hists = self.get_hist(var, bins, year)
                ax.hist(x=bins[:-1], weights=hists[plot_class],
                        bins=bins, label=year, histtype="step", linewidth=1.5,
                        density=True)
                ax.set_title(f"Group {plot_class}")
                ax.legend()
                ax.set_xlabel(var)
                ax.set_ylabel("A.U.")

    def group_shapes(self, var, bins, year, comb_bkg=True):
        with plot(f"{self.fType}_shape_{var}_{year}.png") as ax:
            hists = self.get_hist(var, bins, year, comb_bkg)
            for group, hist in hists.items():
                ax.hist(x=bins[:-1], weights=hist,
                        bins=bins, label=group, histtype="stepfilled", linewidth=1.5,
                        density=True, alpha=0.5, color=self.color_dict[group],
                        edgecolor=self._darkenColor(self.color_dict[group]),
                        hatch="///")

            ax.set_title(f"Year {year}")
            ax.legend()
            ax.set_xlabel(var)
            ax.set_ylabel("A.U.")

    def func(self, var, bins, year, comb_bkg=True):
        with plot(f'{self.fType}_{var}_{year}.png') as ax:
            hists = self.get_hist(var, bins, year, comb_bkg)
            scale = self._find_scales(hists, with_nontrain)
            ax.hist(x=bins[:-1], weights=hists["Signal"]*scale, bins=bins,
                    label=f'Signal x {scale}', histtype="step", linewidth=1.5, )
            ax.hist(x=bins[:-1], weights=hists["Background"], bins=bins, linewidth=1.5,
                    label=f'Background', histtype="step", )

            ax.legend(loc='upper left')
            ax.set_xlabel(var)
            ax.set_ylabel("Events/bin")
            ax.set_title(f'Lumi = {PlotInfo.lumi[year]} ifb')


    def _find_scales(self, variables):
        """**Find scale factor for signal to match rough size of background**

        Increases the scale for signal in a roughly logorithmic
        pattern (1, 5, 10 , 50, 100, ...) to find where the signal and
        background are roughly the same. This is used to make sure the
        plots are scaled well enough to see signal and background

        Args:
          s(float): Number of signal events
          b(float): Number of background events

        Returns:
          int: Scale to be used
        """
        s = sum(variables["Signal"])
        b = sum(variables["Background"])

        ratio = math.log10(b//s)
        scale = 10**int(ratio)
        scale *= 1.5 if (ratio % 1) > math.log10(5) else 1

        return scale
