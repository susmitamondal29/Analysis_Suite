#!/usr/bin/env python3
import math
import awkward1 as ak
import numpy as np

class VarGetter:
    def __init__(self, path):
        self.arr = ak.from_parquet(path)
        self.scale = self.arr.scale_factor

    def return_scale(func):
        def helper(self, *args, with_scale=False, **kwargs):
            if with_scale:
                return func(self, *args, **kwargs), self.scale
            else:
                return func(self, *args, **kwargs)
        return helper

    @return_scale
    def var(self, name):
        return self.arr[name]

    @return_scale
    def num(self, name):
        return ak.count(self.arr[name], axis=1)

    @return_scale
    def num_mask(self, name):
        return ak.count_nonzero(self.arr[name], axis=1)

    @return_scale
    def nth(self, name, n=0, fill=-1):
        arr = ak.pad_none(self.arr[name], n+1, axis=1, clip=True)[:,n]
        return ak.fill_none(arr, fill)

    @return_scale
    def dr(self, part1, idx1, part2, idx2):
        eta2 = self.nth(part1+"_eta", idx1)**2 + self.nth(part2+"_eta", idx2)**2
        phi2 = self.nth(part1+"_phi", idx1)**2 + self.nth(part2+"_phi", idx2)**2
        return np.sqrt(eta2+phi2)

    @return_scale
    def mass(self, part1, idx1, part2, idx2):
        cosh_deta = np.cosh(self.nth(part1+"_eta", idx1) - self.nth(part2+"_eta", idx2))
        cos_dphi = np.cos(self.nth(part1+"_phi", idx1) - self.nth(part2+"_phi", idx2))
        pt = 2*self.nth(part1+"_pt", idx1)*self.nth(part2+"_pt", idx2)
        return pt*(cosh_deta - cos_dphi)

    @return_scale
    def cosDtheta(self, part1, idx1, part2, idx2):
        cosh_eta = np.cosh(self.nth(part1+"_eta", idx1))*np.cosh(self.nth(part2+"_eta", idx2))
        sinh_eta = np.sinh(self.nth(part1+"_eta", idx1))*np.sinh(self.nth(part2+"_eta", idx2))
        cos_dphi = np.cos(self.nth(part1+"_phi", idx1) - self.nth(part2+"_phi", idx2))

        return (cos_dphi - sinh_eta)/cosh_eta

    def flatten(self, name):
        arr_mod, scale_mod = ak.unzip(ak.cartesian([self.arr[name], self.scale]))
        return ak.flatten(arr_mod), ak.flatten(scale_mod),
