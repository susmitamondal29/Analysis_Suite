import awkward1 as ak
import numpy as np
import math
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

    def __iadd__(self, right):
        if isinstance(right, Histogram):
            self.hist += right.hist
            self.breakdown.update({mem: bh_weights()
                                   for mem in right.breakdown.keys()
                                   if mem not in self.breakdown})
            for mem, info in right.breakdown.items():
                self.breakdown[mem] += info
        else:
            pass
        return self

    def __truediv__(self, denom):
        p_raw = (self.vals*self.vals/self.sumw2)
        t_raw = (denom.vals*denom.vals/denom.sumw2)
        ratio = (self.sumw2*denom.vals/(self.vals*denom.sumw2))
        hist = self.hist/denom.hist

        alf = (1-0.682689492137)/2
        lo = np.array([beta.ppf(alf, p, t+1) for p, t in zip(p_raw, t_raw)])
        hi = np.array([beta.ppf(1 - alf, p+1, t) for p, t in zip(p_raw, t_raw)])
        errLo = hist - ratio*lo/(1-lo)
        errHi = ratio*hi/(1-hi) - hist
        hist[np.isnan(hist)], errLo[np.isnan(errLo)], errHi[np.isnan(errHi)] = 0, 0, 0

        return_obj = Histogram("", "", self.hist.axes[0])
        return_obj.hist.view().value = hist
        return_obj.hist.view().variance = (errLo**2 + errHi**2)/2
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

    def fill(self, vals, weight, member=None):
        self.hist.fill(vals, weight=weight)
        if member is not None:
            self.breakdown[member] = bh_weights().fill(sum(weight))

    def set_plot_details(self, group_info):
        name = group_info.get_legend_name(self.group)
        self.name = f'${name}$' if '\\' in name else name
        self.color = group_info.get_color(self.group)

    def get_xrange(self):
        return [self.axis.edges[0], self.axis.edges[-1]]

    def scale(self, scale, forPlot=False):
        if forPlot:
            self.draw_sc *= scale
            # self.name = self.name.split(" x")[0] + " x {}".format(int(self.draw_sc))
        else:
            self.hist *= scale

            for mem, info in self.breakdown.items():
                self.breakdown[mem] *= scale

    def integral(self):
        return self.hist.sum(flow=True).value

    def getInputs(self, **kwargs):
        return dict({"x": self.axis.centers, "xerr": self.axis.widths/2,
                "y": self.draw_sc*self.vals, "ecolor": self.color,
                "yerr": self.draw_sc*self.err, 'fmt': 'o',
                "color": self.color, "barsabove": True, "label": self.name,
                'markersize': 4}, **kwargs)

    def getInputsHist(self, **kwargs):
        # bins = self.bins - 0.5 if self.isMult else self.bins
        return dict({"weights": self.draw_sc*self.vals,
                     "bins": self.axis.edges, "x": self.axis.centers,
                     "color": self.color, # 'align': "mid"
                     "histtype": "step"},
                    **kwargs)

    def getInputsError(self, **kwargs):
        # bins = self.bins - 0.5 if self.isMult else self.bins
        bottom = self.vals - self.err
        return dict({"weights": 2*self.err, "x": self.axis.centers,
                "bins": self.axis.edges, 'bottom': bottom,
                "histtype": 'stepfilled', "color": self.color,
                'align': 'mid', 'stacked': True, "hatch": '//',
                "alpha": 0.4, "label":self.name}, **kwargs)

    def get_int_err(self, sqrt_err=False, roundDigit=2):
        tot = self.hist.sum()
        err = math.sqrt(tot.variance) if sqrt_err else tot.variance
        return np.round(np.array([tot.value, err]), roundDigit)
