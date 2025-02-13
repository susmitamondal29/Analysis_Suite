import awkward as ak
import numpy as np
import math
from copy import copy
import boost_histogram as bh
from boost_histogram.accumulators import WeightedSum as bh_weights
from scipy.stats import beta
import warnings

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

    def __mul__(self, right):
        hist = Histogram(self.group, *self.hist.axes)
        hist.hist = right*self.hist
        return hist

    def __rmul__(self, right):
        hist = Histogram(self.group, *self.hist.axes)
        hist.hist = right*self.hist
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ratio = np.nan_to_num(self.vals/denom.vals)
            error2 = ratio**2*(self.err_ratio + denom.err_ratio)

        return_obj = Histogram("", *self.hist.axes)
        return_obj.hist.values()[:] = ratio
        return_obj.hist.variances()[:] = error2
        return return_obj

    def __bool__(self):
        return not self.hist.empty()

    def __getstate__(self):
        return {"hist": self.hist, "group": self.group,
                "color": self.color, "name": self.name,
                "breakdown": self.breakdown, "draw_sc": self.draw_sc}

    def __setstate__(self, state):
        self.hist = state["hist"]
        self.group = state["group"]
        self.color = state["color"]
        self.name = state["name"]
        self.breakdown = state["breakdown"]
        self.draw_sc = state["draw_sc"]

    def __getattr__(self, attr):
        if attr == 'axis':
            return self.hist.axes[0]
        elif attr == 'axes':
            return self.hist.axes
        elif attr == 'vals':
            return self.hist.view().value
        elif attr == 'err':
            return np.sqrt(self.hist.view().variance)
        elif attr == 'sumw2':
            return self.hist.view().variance
        elif attr == 'err_ratio':
            return np.nan_to_num(self.sumw2/self.vals**2)
        else:
            raise Exception()

    @staticmethod
    def efficiency(top, bot):
        alf = (1-0.682689492137)/2
        aa = top.vals*bot.vals/bot.sumw2+1
        bb = (bot.vals-top.vals)*bot.vals/bot.sumw2+1

        eff = np.array([beta.mean(p, t) for p, t in zip(aa, bb)])

        lo = np.array([beta.ppf(alf, p, t) for p, t in zip(aa, bb)])
        hi = np.array([beta.ppf(1 - alf, p, t) for p, t in zip(aa, bb)])
        error2 = (eff-lo)**2 + (hi-eff)**2

        return_obj = Histogram("", *top.hist.axes)
        return_obj.hist.values()[:] = eff
        return_obj.hist.variances()[:] = error2
        return return_obj


    def set_metadata(self, other):
        self.group = other.group
        self.color = other.color
        self.name = other.name
        self.draw_sc = other.draw_sc

    def project(self, ax):
        new_hist = Histogram(self.group, self.hist.axes[0])
        new_hist.hist = self.hist.project(ax)
        new_hist.set_metadata(self)
        return new_hist

    def fill(self, *vals, weight, member=None):
        self.hist.fill(*vals, weight=weight)
        if member is not None:
            self.breakdown[member] = bh_weights().fill(weight)

    def set_plot_details(self, group_info):
        if isinstance(group_info, list):
            self.name = group_info[0]
            self.color = group_info[1]
        else:
            name = group_info.get_legend_name(self.group)
            self.name = f'${name}$' if '\\' in name else name
            self.color = group_info.get_color(self.group)

    def get_xrange(self):
        return [self.axis.edges[0], self.axis.edges[-1]]

    def scale(self, scale, changeName=False, forPlot=False):
        if changeName:
            str_scale = str(scale) if isinstance(scale, int) else f'{scale:0.2f}'
            self.name = self.name.split(" x")[0] + f" x {str_scale}"
        if forPlot:
            self.draw_sc *= scale
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

    def plot_2d(self, pad, **kwargs):
        if not self or pad is None:
            return

        xx = np.tile(self.axes[0].edges, (len(self.axes[1])+1, 1))
        yy = np.tile(self.axes[1].edges, (len(self.axes[0])+1, 1)).T
        color_plot = pad.pcolormesh(xx, yy, self.vals.T, shading='flat', **kwargs)

        xstart, xend = self.get_xrange()
        min_size = (xend-xstart)/9
        min_ysize = (self.axes[1].edges[-1]-self.axes[1].edges[0])/14

        for j, y in enumerate(self.axes[1].centers):
            offset = False
            for i, x in enumerate(self.axes[0].centers):
                ha = 'center' if i != 0 else 'left'
                if i == 0:
                    x = xstart
                elif offset:
                    offset = False
                elif self.axis.widths[i-1] < min_size and self.axis.widths[i] < min_size:
                    offset = True

                ytot = y - offset*min_ysize
                val_str = f'{self.vals[i,j]:.3f}\n$\pm${self.err[i,j]:.3f}'
                text = pad.text(x, ytot, val_str, fontsize='x-small', ha=ha, va='center')
        return color_plot


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
