#!/usr/bin/env python3
import awkward as ak
import uproot as uproot
import numpy as np
from copy import copy

from .basegetter import BaseGetter

class VarGetter(BaseGetter):
    single_branch = ["run", "event", "lumiBlock"]

    def __init__(self, filename, treename, group, xsec, syst=0, systName=""):
        super().__init__()
        self.syst = syst
        self.syst_bit = 2**self.syst
        self.systName = ""
        self.part_name = []
        self.arr = dict()
        self.parts = dict()
        self.branches = []

        f = uproot.open(filename)
        if group not in f or treename not in f[group]:
            return
        self.tree = f[group][treename]
        self.branches = [key for key, array in self.tree.items() if len(array.keys()) == 0]
        self.part_name = np.unique([br.split('/')[0] for br in self.branches if '/' in br])
        self._base_mask = ak.to_numpy(self._get_var("PassEvent"))
        self._mask = copy(self._base_mask)
        self._scale = ak.to_numpy(self._get_var("weight"))
        self.setSyst(systName)

        if group == "data":
            _, unique_idx = np.unique(ak.to_numpy(self["event"]), return_index=True)
            self.mask = np.in1d(np.arange(len(self)), unique_idx)
            self._base_mask = copy(self._mask)
        else:
            sumw = sum(f[group]["sumweight"].values())
            self._scale = xsec/sumw*self._scale

    def _get_var(self, name):
        return self.tree[name].array()[:, self.syst]

    def _get_var_nosyst(self, name):
        return self.tree[name].array()

    def __getitem__(self, key):
        if key in self.part_name:
            if key not in self.parts:
                self.parts[key] = Particle(key, self)
            return self.parts[key]
        elif not self.exists(key):
            raise AttributeError(f'{key} not found')
        elif key not in self.arr:
            if "/" in key or key in self.single_branch:
                self.arr[key] = self._get_var_nosyst(key)
            else:
                self.arr[key] = self._get_var(key)
        return self.arr[key][self.mask]

    def setSyst(self, systName):
        if systName in ["JES", "JER"]:
            jec = systName.lower().split('_')
            updown = {"down": "first", "up": "second"}
            self.jec_var = f'jec/{jec[1]}.{updown[jec[2]]}'
        else:
            self.jec_var = ""

    def mergeParticles(self, merge, *parts):
        self.part_name = np.append(self.part_name, merge)
        self.parts[merge] = MergeParticle([self[part] for part in parts])


    def exists(self, branch):
        return branch in self.branches

    def close(self):
        self.tree.close()

    # Function to combine things

    @staticmethod
    def combine(arr1, arr2):
        return ak.sum(ak.unzip(ak.cartesian([arr1, arr2], axis=-1)), axis=0)

    def dr(self, part1, idx1, part2, idx2):
        deta = self[part1]["eta", idx1] - self[part2]["eta", idx2]
        dphi = self.dphi(part1, idx1, part2, idx2)
        return np.sqrt(deta**2 + dphi**2)

    def dphi(self, part1, idx1, part2, idx2):
        dphi = ak.to_numpy(self[part1]["phi", idx1] - self[part2]["phi", idx2])
        dphi[dphi > np.pi] = dphi[dphi > np.pi] - np.pi
        dphi[dphi < -np.pi] = dphi[dphi < -np.pi] + np.pi
        return dphi

    def cosDtheta(self, part1, idx1, part2, idx2):
        cosh_eta = np.cosh(self[part1]['eta', idx1]) * np.cosh(self[part2]['eta', idx2])
        sinh_eta = np.sinh(self[part1]['eta', idx1]) * np.sinh(self[part2]['eta', idx2])
        cos_dphi = np.cos(self[part1]['phi', idx1] - self[part2]['phi', idx2])
        return (cos_dphi + sinh_eta)/cosh_eta

    def mass(self, part1, idx1, part2, idx2):
        energy = self[part1]['energy', idx1] + self[part2]['energy', idx2]
        px = self[part1]['px', idx1] + self[part2]['px', idx2]
        py = self[part1]['py', idx1] + self[part2]['py', idx2]
        pz = self[part1]['pz', idx1] + self[part2]['pz', idx2]
        return np.sqrt(energy**2 - px**2 - py**2 - pz**2)

    def top_mass(self, part1, part2):
        energy = self.combine(self[part1].energy(), self[part2].energy()) + self["Met"]
        px = self.combine(self[part1].px(), self[part2].px()) + self["Met"]*np.cos(self["Met_phi"])
        py = self.combine(self[part1].py(), self[part2].py()) + self["Met"]*np.sin(self["Met_phi"])
        pz = self.combine(self[part1].pz(), self[part2].pz())
        top = np.sqrt(energy**2 - px**2 - py**2 - pz**2)
        return top[ak.argmin(np.abs(top - 172.76), axis=-1, keepdims=True)][:, 0]


class Particle:
    def __init__(self, name, vg):
        self.vg = vg
        self.name = name
        self._mask = np.bitwise_and(vg._get_var_nosyst(f'{self.name}/syst_bitMap'), vg.syst_bit) != 0

    # Getter functions

    def __getattr__(self, var):
        if var == "pt":
            return self._pt()
        return self.vg[f'{self.name}/{var}'][self.mask]

    def __getitem__(self, idx):
        pad = False
        if len(idx) == 2:
            var, idx = idx
        else:
            var, idx, pad = idx

        if callable(getattr(self, var)):
            return getattr(self, var)(idx)
        else:
            return self._get_val(var, idx, pad)

    def _get_val(self, var, idx, pad=False):
        if pad:
            vals = ak.pad_none(self.vg[f'{self.name}/{var}'][self.mask], idx+1)
        elif idx == -1:
            return self.vg[f'{self.name}/{var}'][self.mask]
        else:
            vals = self.vg[f'{self.name}/{var}'][self.mask][self.num() > idx]
        return ak.to_numpy(vals[:, idx])

    # Special function for allowing jec in pt

    def _pt(self, idx=-1):
        if self.vg.jec_var and "Jet" in self.name:
            return self._get_val('pt', idx) * self[f'{self.vg.jec_var}']
        else:
            return self._get_val('pt', idx)

    # def get_hist(self, var, idx, *args):
    #     return self._get_val(var, idx, *args), self.scale(idx)

    # def get_hist2d(self, var1, var2, idx, *args):
    #     return (self._get_val(var1, idx, *args), self._get_val(var2, idx, *args)), self.scale(idx)

    @property
    def mask(self):
        return self._mask[self.vg.mask]

    def scale(self, n):
        if n == -1:
            return ak.broadcast_arrays(self.vg.scale, self.pt)[0]
        else:
            return self.vg.scale[self.num() > n]

    # Functions for a particle

    def abseta(self, idx=-1):
        return np.abs(self['eta', idx])

    def num(self):
        return ak.to_numpy(ak.count(self.mask, axis=1))

    def px(self, idx=-1):
        return self['pt', idx]*np.cos(self['phi', idx])

    def py(self, idx=-1):
        return self['pt', idx]*np.sin(self['phi', idx])

    def pz(self, idx=-1):
        return self['pt', idx]*np.sinh(self['eta', idx])

    def energy(self, idx=-1):
        return np.sqrt(self['mass', idx]**2 + (self['pt', idx]*np.cosh(self['eta', idx]))**2)

    def mt(self, idx=-1):
        mask = self.num() > idx
        angle_part = 1-np.cos(self['phi', idx] - self.vg["Met_phi"][mask])
        return np.sqrt(2*self['pt', idx] * self.vg["Met"][mask] * angle_part)

    def pt_ratio(self, idx=-1):
        return 1/(1+self["ptRatio", idx])


class MergeParticle:
    def __init__(self, parts):
        self.parts = parts
        self._idx_sort = ak.argsort(self.get_list("pt"), ascending=False)
        self.vg = self.parts[0].vg
        self.__pad__ = False

    def pad(self):
        self.__pad__ = True

    @property
    def mask(self):
        return self.vg.mask[self.vg._base_mask]

    @property
    def idx_sort(self):
        return self._idx_sort[self.mask]

    def __getattr__(self, var):
        return self.get_list(var)[self.idx_sort]

    def __getitem__(self, idx):
        pad = False
        if len(idx) == 2:
            var, idx = idx
        else:
            var, idx, pad = idx
        vals = self.get_list(var)[self.idx_sort]
        if pad:
            return ak.to_numpy(ak.pad_none(vals, idx+1)[:, idx])
        else:
            return vals[ak.num(vals) > idx, idx]

    def num(self):
        return ak.num(self.idx_sort, axis=-1)

    def scale(self, idx):
        return self.vg.scale[ak.num(self.pt, axis=-1) > idx]

    def get_list(self, var):
        if callable(getattr(self.parts[0], var)):
            return ak.concatenate((getattr(part, var)() for part in self.parts), axis=-1)
        else:
            return ak.concatenate((part.__getattr__(var) for part in self.parts), axis=-1)

    def get_hist(self, var, idx):
        return self[var, idx], self.scale(idx)

    def get_hist2d(self, var1, var2, idx):
        return (self[var1, idx], self[var2, idx]), self.scale(idx)
