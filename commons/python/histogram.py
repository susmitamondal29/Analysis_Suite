import awkward1 as ak
import numpy as np
import math
from copy import copy
import boost_histogram as bh
from boost_histogram.accumulators import WeightedSum as bh_weights
from scipy.stats import beta


class Histogram:
    def __init__(self, group, *args, **kwargs):
        self.hist = bh.Histogram(*args, storage=bh.storage.Weight())
        self.breakdown = dict()
        self.group = group
        self.color = "k" if "color" not in kwargs else kwargs["color"]
        self.name = ""
        self.draw_sc = 1.

    def __add__(self, right):
        hist = Histogram(self.group, self.axis)
        hist.hist = self.hist + right.hist
        return hist

    def __sub__(self, right):
        hist = Histogram(self.group, self.axis)
        hist.hist = self.hist + (-1)*right.hist
        return hist

    def __iadd__(self, right):
        if isinstance(right, Histogram):
            self._set_hist(right.hist)
            self.breakdown.update({mem: bh_weights()
                                   for mem in right.breakdown.keys()
                                   if mem not in self.breakdown})
            for mem, info in right.breakdown.items():
                self.breakdown[mem] += info
        elif isinstance(right, bh.Histogram):
            self._set_hist(right)
        return self

    def _set_hist(self, hist):
        if not self:
            self.hist = copy(hist)
        else:
            self.hist += hist

    def __truediv__(self, denom):
        p_raw = (self.vals*self.vals/self.sumw2)
        t_raw = (denom.vals*denom.vals/denom.sumw2)
        ratio = (self.sumw2*denom.vals/(self.vals*denom.sumw2))
        hist = self.vals/denom.vals

        alf = (1-0.682689492137)/2
        lo = np.array([beta.ppf(alf, p, t+1) for p, t in zip(p_raw, t_raw)])
        hi = np.array([beta.ppf(1 - alf, p+1, t) for p, t in zip(p_raw, t_raw)])
        errLo = hist - ratio*lo/(1-lo)
        errHi = ratio*hi/(1-hi) - hist
        hist[np.isnan(hist)], errLo[np.isnan(errLo)], errHi[np.isnan(errHi)] = 0, 0, 0
        return_obj = Histogram("", self.hist.axes[0])
        return_obj.hist.values()[:] = hist
        return_obj.hist.variances()[:] = (errLo**2 + errHi**2)/2
        return return_obj

    def __bool__(self):
        return not self.hist.empty()

    def __getattr__(self, attr):
        if attr == 'axis':
            return self.hist.axes[0]
        elif attr == 'vals':
            return self.hist.view().value
        elif attr == 'err':
            return np.sqrt(self.hist.view().variance)
        elif attr == 'sumw2':
            return self.hist.view().variance
        else:
            raise Exception()

    def project(self, ax):
        new_hist = Histogram(self.group, self.hist.axes[0])
        new_hist.hist = self.hist.project(ax)
        return new_hist

    def fill(self, *vals, weight, member=None):
        self.hist.fill(*vals, weight=weight)
        if member is not None:
            self.breakdown[member] = bh_weights().fill(weight)

    def set_plot_details(self, group_info):
        name = group_info.get_legend_name(self.group)
        self.name = f'${name}$' if '\\' in name else name
        self.color = group_info.get_color(self.group)

    def get_xrange(self):
        return [self.axis.edges[0], self.axis.edges[-1]]

    def scale(self, scale, forPlot=False):
        if forPlot:
            self.draw_sc *= scale
            self.name = self.name.split(" x")[0] + " x {}".format(int(self.draw_sc))
        else:
            self.hist *= scale
            for mem, info in self.breakdown.items():
                self.breakdown[mem] *= scale

    def integral(self, flow=True):
        return self.hist.sum(flow=flow).value

    def plot_points(self, pad, **kwargs):
        if not self or pad is None:
            return
        pad.errorbar(x=self.axis.centers, xerr= self.axis.widths/2,
                     y=self.draw_sc*self.vals, ecolor=self.color,
                     yerr=self.draw_sc*self.err, fmt='o',
                     color=self.color, barsabove=True, label=self.name,
                     markersize=4, **kwargs)

    def plot_band(self, pad, **kwargs):
        if not self or pad is None:
            return
        pad.hist(weights=2*self.err, x=self.axis.centers,
                 bins=self.axis.edges,
                 bottom=self.vals - self.err,
                 histtype='stepfilled', color=self.color,
                 align='mid', stacked=True, hatch='//',
                 alpha=0.4, label=self.name, **kwargs)

    def get_int_err(self, sqrt_err=False, roundDigit=2):
        tot = self.hist.sum()
        err = math.sqrt(tot.variance) if sqrt_err else tot.variance
        return np.round(np.array([tot.value, err]), roundDigit)
