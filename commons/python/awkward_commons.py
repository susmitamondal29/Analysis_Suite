#!/usr/bin/env python3
import math
import awkward1 as ak
import uproot4 as uproot
import numpy as np
from .info import FileInfo

class VarGetter:
    def __init__(self, path, group, syst=0):
        self.syst = syst
        self.syst_bit = 2**syst
        with uproot.open(path) as f:
            branches = [key for key, array in f[group]["Analyzed"].items()
                        if len(array.keys()) == 0]
            analysis = f[group]["Analysis"].member("fTitle")
            year = f[group]["Year"].member("fTitle")
            info = FileInfo(analysis=analysis, year=year)
            self.xsec = info.get_xsec(group)
            self.sumw = sum(f[group]["sumweight"].values())
            if f[group]["Analyzed"].num_entries != 0:
                analyzed = f[group]["Analyzed"]
                passMask = analyzed["PassEvent"].array()[:, self.syst]
                self.arr = analyzed.arrays(branches)[passMask]
                self.scale = self.arr["weight"][:,self.syst]*self.xsec/self.sumw
            else:
                self.arr = ak.Array([])
                self.scale = ak.Array([])

    def __add__(self, other):
        sumwTot = self.sumw + other.sumw
        self.arr = ak.concatenate((self.arr, other.arr))
        self.scale = ak.concatenate((self.sumw*self.scale, other.sumw*other.scale))/sumwTot
        self.sumw = sumwTot
        return self

    def __len__(self):
        return len(self.scale)

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

    def get_part_mask(self, part):
        return np.bitwise_and(self.arr["{}/syst_bitMap".format(part)], self.syst_bit) != 0

    def num(self, part):
        return ak.to_numpy(ak.count(self.get_part_mask(part), axis=1))

    def pt(self, part, n, fill=-1):
        return self.nth(part, "pt", n, fill)

    def eta(self, part, n, fill=-1):
        return self.nth(part, "eta", n, fill)

    def phi(self, part, n, fill=-1):
        return self.nth(part, "phi", n, fill)

    def mass(self, part, n, fill=-1):
        return self.nth(part, "mass", n, fill)

    def nth(self, part, name, n=0, fill=-1):
        var = self.arr[f'{part}/{name}'][self.get_part_mask(part)]
        return ak.to_numpy(ak.fill_none(ak.pad_none(var, n+1, axis=1, clip=True)[:,n], fill))

    def dr(self, part1, idx1, part2, idx2):
        eta2 = self.eta(part1, idx1)**2 + self.eta(part2, idx2)**2
        phi2 = self.phi(part1, idx1)**2 + self.phi(part2, idx2)**2
        return np.sqrt(eta2+phi2)

    def mass(self, part1, idx1, part2, idx2):
        cosh_deta = np.cosh(self.eta(part1, idx1) - self.eta(part2, idx2))
        cos_dphi = np.cos(self.phi(part1, idx1) - self.phi(part2, idx2))
        pt = 2*self.pt(part1, idx1)*self.pt(part2, idx2)
        return pt*(cosh_deta - cos_dphi)

    def cosDtheta(self, part1, idx1, part2, idx2):
        cosh_eta = np.cosh(self.eta(part1, idx1))*np.cosh(self.eta(part2, idx2))
        sinh_eta = np.sinh(self.eta(part1, idx1))*np.sinh(self.eta(part2, idx2))
        cos_dphi = np.cos(self.phi(part1, idx1) - self.phi(part2, idx2))

        return (cos_dphi - sinh_eta)/cosh_eta

    def var(self, name):
        return ak.to_numpy(self.arr[name][:,self.syst])

    ##### Need to fix

    def mwT(self, part):
        part_phi = self.arr[f'{part}/phi'][self.get_part_mask(part)]
        part_pt = self.arr[f'{part}/pt'][self.get_part_mask(part)]
        cos_angles = np.cos(part_phi-self.var("Met_phi"))
        close_mask = ak.argmax(cos_angles, axis=-1) == ak.local_index(cos_angles, axis=-1)
        close_pt = self.flatten(part_pt[close_mask])

        return np.sqrt(2*self.var("Met")*close_pt*(1 - self.flatten(cos_angles[close_mask])))
    
    def flatten(self, arr):
        return ak.to_numpy(ak.flatten(arr))
        # arr_mod, scale_mod = ak.unzip(ak.cartesian([self.arr[name], self.scale]))
        # return ak.to_numpy(ak.flatten(arr_mod))
