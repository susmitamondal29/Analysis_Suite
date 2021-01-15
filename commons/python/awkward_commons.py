#!/usr/bin/env python3
import math
import awkward1 as ak
import uproot4 as uproot
import numpy as np

class VarGetter:
    def __init__(self, path):
        with uproot.open(path) as f:
            self.group = [key for key in f.keys() if "/" not in key][0]
            if ";" in self.group:
                self.group = self.group[:self.group.index(';')]
            branches = [key for key, array in f[self.group]["Analyzed"].items()
                        if len(array.keys()) == 0]
            self.arr = f[self.group]["Analyzed"].arrays(branches)
            self.xsec = float(f[self.group]["xsec"].member("fTitle"))
            self.sumw = sum(f[self.group]["sumweight"].values())
            self.scale = self.arr["weight"]*self.xsec/self.sumw



    def __add__(self, other):
        sumwTot = self.sumw + other.sumw
        self.arr = ak.concatenate((self.arr, other.arr))
        self.scale = ak.concatenate((self.sumw*self.scale, other.sumw*other.scale))/sumwTot
        print(ak.type(self.scale))
        self.sumw = sumwTot
        return self

    def setup_scale(self):
        self.scale *= self.xsec/self.sumw


    def return_scale(func):
        def helper(self, with_scale=False, *args, **kwargs):
            print(args, kwargs, with_scale)
            if with_scale:
                return func(self, *args, **kwargs), self.scale
            else:
                return func(self, *args, **kwargs)
        return helper


    def var(self, name):
        return self.arr[name]


    def num(self, name):
        return ak.count(self.arr[name], axis=1)


    def num_mask(self, name):
        return ak.count_nonzero(self.arr[name], axis=1)


    def nth(self, name, n=0, fill=-1):
        arr = ak.pad_none(self.arr[name], n+1, axis=1, clip=True)[:,n]
        return ak.fill_none(arr, fill)


    def dr(self, part1, idx1, part2, idx2):
        eta2 = self.nth(part1+"_eta", idx1)**2 + self.nth(part2+"_eta", idx2)**2
        phi2 = self.nth(part1+"_phi", idx1)**2 + self.nth(part2+"_phi", idx2)**2
        return np.sqrt(eta2+phi2)


    def mass(self, part1, idx1, part2, idx2):
        cosh_deta = np.cosh(self.nth(part1+"_eta", idx1) - self.nth(part2+"_eta", idx2))
        cos_dphi = np.cos(self.nth(part1+"_phi", idx1) - self.nth(part2+"_phi", idx2))
        pt = 2*self.nth(part1+"_pt", idx1)*self.nth(part2+"_pt", idx2)
        return pt*(cosh_deta - cos_dphi)


    def cosDtheta(self, part1, idx1, part2, idx2):
        cosh_eta = np.cosh(self.nth(part1+"_eta", idx1))*np.cosh(self.nth(part2+"_eta", idx2))
        sinh_eta = np.sinh(self.nth(part1+"_eta", idx1))*np.sinh(self.nth(part2+"_eta", idx2))
        cos_dphi = np.cos(self.nth(part1+"_phi", idx1) - self.nth(part2+"_phi", idx2))

        return (cos_dphi - sinh_eta)/cosh_eta

    def flatten(self, name):
        arr_mod, scale_mod = ak.unzip(ak.cartesian([self.arr[name], self.scale]))
        return ak.flatten(arr_mod), ak.flatten(scale_mod),
