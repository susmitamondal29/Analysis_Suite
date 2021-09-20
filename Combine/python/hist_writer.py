#!/usr/bin/env python3
import numpy
from uproot_methods.classes.TH1 import Methods

def from_boost(histogram, title=""):
    class TH1(Methods, list):
        pass

    class TAxis(object):
        def __init__(self, edges):
            self._fNbins = len(edges) - 1
            self._fXmin = edges[0]
            self._fXmax = edges[-1]
            if numpy.array_equal(edges, numpy.linspace(self._fXmin, self._fXmax, len(edges), dtype=edges.dtype)):
                self._fXbins = numpy.array([], dtype=">f8")
            else:
                self._fXbins = edges.astype(">f8")

    centers = histogram.axes[0].centers

    out = TH1.__new__(TH1)

    out._fTitle = title
    out._classname = "TH1F"

    out._fXaxis = TAxis(histogram.axes[0].edges)
    out._fEntries = out._fTsumw = histogram.sum().value
    out._fTsumw2 = histogram.sum().variance
    out._fTsumwx = (histogram.values() * centers).sum()
    out._fTsumwx2 = (histogram.values() * centers**2).sum()

    out.extend(histogram.values(flow=True))
    out._fSumw2 = histogram.variances(flow=True)
 # out._classname, content = _histtype(content)

    return out
