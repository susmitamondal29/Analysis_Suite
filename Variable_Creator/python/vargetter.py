#!/usr/bin/env python3
import awkward as ak
import uproot as uproot
import numpy as np
from copy import copy

class VarGetter:
    single_branch = ["run", "event", "lumiBlock"]

    def __init__(self, filename, treename, group, xsec, syst=0):
        self.syst = syst
        self.syst_bit = 2**self.syst
        self.systName = ""
        self._mask = None
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

        if group == "data":
            _, unique_idx = np.unique(ak.to_numpy(self["event"]), return_index=True)
            self.mask = np.in1d(np.arange(len(self)), unique_idx)
            self._base_mask = copy(self._mask)
        else:
            sumw = sum(f[group]["sumweight"].values())
            self._scale = xsec/sumw*self._scale

    def __bool__(self):
        return self._mask is not None

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

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __len__(self):
        return np.count_nonzero(self.mask)

    def setSyst(self, systName):
        self.systName = systName
        if systName in ["JES", "JER"]:
            jec = self.vg.systName.lower().split('_')
            updown = {"down": "first", "up": "second"}
            self.jec_var = f'jec/{jec[1]}.{updown[jec[2]]}'
        else:
            self.jec_var = ""

    def mergeParticles(self, merge, part1, part2):
        self.part_name = np.append(self.part_name, merge)
        self.parts[merge] = MergeParticle(self[part1], self[part2])

    # Scale related functions

    @property
    def scale(self):
        return self._scale[self.mask]

    @scale.setter
    def scale(self, scale):
        if isinstance(scale, tuple):
            scale, mask = scale
            self._scale[self.get_submask(mask)] = scale
        else:
            self._scale[self.mask] = scale

    def get_submask(self, mask):
        submask = copy(self.mask)
        submask[submask] *= mask
        return submask

    # Mask related functions

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        self._mask[self._mask] *= mask

    def clear_mask(self):
        self._mask = copy(self._base_mask)


    def get_hist(self, var):
        if not hasattr(self, var):
            raise AttributeError
        return self[var], self.scale

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
        dphi = self[part1]["phi", idx1] - self[part2]["phi", idx2]
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

    def padding(func):
        def inner(self, *args, pad=False, fill=-1):
            print(args)
            if pad:
                self.__pad__ = True
                vals = ak.fill_none(func(self, *args), fill)
                self.__pad__ = False
                return ak.to_numpy(vals)
            else:
                return func(self, *args)
        return inner

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

    def abseta(self, idx):
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

    def mt(self, idx):
        mask = self.num() > idx
        angle_part = 1-np.cos(self['phi', idx] - self.vg["Met_phi"][mask])
        return np.sqrt(2*self['pt', idx] * self.vg["Met"][mask] * angle_part)

    def pt_ratio(self, idx=-1):
        return 1/(1+self["ptRatio", idx])


class MergeParticle:
    def __init__(self, part1, part2):
        self.part1 = part1
        self.part2 = part2
        self.idx_sort = ak.argsort(ak.concatenate((part1.pt, part2.pt), axis=-1), ascending=False)
        self.__pad__ = False

    def pad(self):
        self.__pad__ = True

    def __getattr__(self, var):
        if callable(getattr(self.part1, var)):
            return lambda : ak.concatenate((getattr(self.part1, var)(), getattr(self.part2, var)()), axis=-1)[self.idx_sort]
        else:
            return ak.concatenate((self.part1.__getattr__(var), self.part2.__getattr__(var)), axis=-1)[self.idx_sort]

    def __getitem__(self, idx):
        var, idx = idx
        if callable(getattr(self.part1, var)):
            vals = ak.concatenate((getattr(self.part1, var)(), getattr(self.part2, var)()), axis=-1)[self.idx_sort]
        else:
            vals = ak.concatenate((self.part1.__getattr__(var), self.part2.__getattr__(var)), axis=-1)[self.idx_sort]
        if self.__pad__:
            vals = ak.pad_none(vals, idx+1)
        return ak.to_numpy(vals[:, idx])

