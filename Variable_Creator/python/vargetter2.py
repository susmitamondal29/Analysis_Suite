#!/usr/bin/env python3
import math
import awkward as ak
import uproot as uproot
import numpy as np
import itertools
from analysis_suite.commons.configs import get_metadata
from analysis_suite.commons.info import FileInfo
from dataclasses import dataclass
from typing import Callable
from copy import copy

@dataclass
class Variable:
    func: Callable[..., dict]
    inputs: tuple

    def apply(self, arr):
        if isinstance(self.inputs, str):
            return self.func(arr, self.inputs)
        else:
            return self.func(arr, *self.inputs)

    def getType(self):
        isInt = "num" in repr(self.func) or "n_" in self.inputs
        return "int" if isInt else "float"

class VarGetter:
    single_branch = ["run", "event", "lumiBlock"]

    def __init__(self, filename, treename, group, xsec, syst=0):
        self.syst = syst
        self.syst_bit = 2**self.syst
        f = uproot.open(filename)
        if group not in f:
            exit()
        self.tree = f[group][treename]
        self.branches = [key for key, array in self.tree.items()
                         if len(array.keys()) == 0]
        self.part_name = np.unique([br.split('/')[0] for br in self.branches if '/' in br])

        self.arr = dict()
        self.parts = dict()
        self._base_mask = ak.to_numpy(self._get_var("PassEvent"))
        self._mask = copy(self._base_mask)
        self._scale = ak.to_numpy(self._get_var("weight"))

        if group == "data":
            _, unique_idx = np.unique(ak.to_numpy(self["event"]), return_index=True)
            self.mask = np.in1d(np.arange(len(self)), unique_idx)
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
            return
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

    @property
    def scale(self):
        return self._scale[self.mask]

    @scale.setter
    def scale(self, scale):
        self._scale[self.mask] = scale

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        self._mask[self._mask] *= mask

    def get_hist(self, var):
        if not hasattr(self, var):
            raise AttributeError
        return self[var], self.scale

    def clear_mask(self):
        self._mask = copy(self._base_mask)

    def exists(self, branch):
        return branch in self.branches


class Particle:
    def __init__(self, name, vg):
        self.vg = vg
        self.name = name
        self._mask = np.bitwise_and(vg._get_var_nosyst(f'{self.name}/syst_bitMap'), vg.syst_bit) != 0

    def __getattr__(self, var):
        return self.vg[f'{self.name}/{var}'][self.mask]

    def __getitem__(self, idx):
        var, idx = idx
        return ak.to_numpy(self.vg[f'{self.name}/{var}'][self.mask][self.num() > idx][:, idx])

    def check_compatibility(func):
        def inner(self, idx, part, pidx):
            if not np.all((part.num()[self.num() > idx] > pidx)):
                raise Exception
            return func(self, idx, part, pidx)
        return inner

    def pad(self, var, idx, fill=-1):
        vals = ak.fill_none(ak.pad_none(self.vg[f'{self.name}/{var}'][self.mask], idx+1), fill)
        return vals[:, idx]

    def _get_val(self, var, idx, *args):
        if not hasattr(self, var):
            raise AttributeError
        if callable(getattr(self, var)):
            return getattr(self, var)(idx, *args)
        else:
            return self[var, idx]

    def get_hist(self, var, idx, *args):
        return self._get_val(var, idx, *args), self.scale(idx)

    def get_hist2d(self, var1, var2, idx, *args):
        return (self._get_val(var1, idx, *args), self._get_val(var2, idx, *args)), self.scale(idx)

    @property
    def mask(self):
        return self._mask[self.vg.mask]

    def scale(self, n):
        return self.vg.scale[self.num() > n]

    def abseta(self, idx):
        return np.abs(self['eta', idx])

    def num(self):
        return ak.to_numpy(ak.count(self.mask, axis=1))

    def energy(self, idx):
        return np.sqrt(self['mass', idx]**2 + (self['pt', idx]*np.cosh(self['eta', idx]))**2)

    def mt(self, idx):
        mask = self.num() > idx
        angle_part = 1-np.cos(self['phi', idx] - self.vg["Met_phi"][mask])
        return np.sqrt(2*self['pt', idx] * self.vg["Met"][mask] * angle_part)

    @check_compatibility
    def dr(self, idx, part, pidx):
        mask = self.num() > idx
        eta2 = (self["eta", idx] - part["eta", pidx][mask])**2
        phi2 = self.dphi(idx, part, idx)**2
        return np.sqrt(eta2+phi2)

    @check_compatibility
    def dphi(self, idx, part, pidx):
        mask = self.num() > idx
        dphi = self['phi', idx] - part['phi', pidx][mask]
        dphi[dphi > np.pi] = dphi[dphi > np.pi] - np.pi
        dphi[dphi < np.pi] = dphi[dphi < np.pi] + np.pi
        return dphi

    @check_compatibility
    def mass(self, idx, part, pidx):
        mask = self.num() > idx
        # This assumes E ~ p or p >> m (true for light particles)
        cosh_deta = np.cosh(self['eta', idx] - part['eta', pidx][mask])
        cos_dphi = np.cos(self['phi', idx] - part['phi', pidx][mask])
        pt = 2*self['pt', idx] * part['pt', pidx][mask]
        return np.sqrt(pt*(cosh_deta - cos_dphi))

    @check_compatibility
    def cosDtheta(self, idx, part, pidx):
        mask = self.num() > idx
        cosh_eta = np.cosh(self['eta', idx]) * np.cosh(part['eta', pidx][mask])
        sinh_eta = np.sinh(self['eta', idx]) * np.sinh(part['eta', pidx][mask])
        cos_dphi = np.cos(self['phi', idx] - part['phi', pidx][mask])
        return (cos_dphi - sinh_eta)/cosh_eta

    @check_compatibility
    def true_mass(self, idx, part, pidx):
        mask = self.num() > idx
        m1 = self['mass', idx]
        m2 = part['mass', pidx][mask]
        e1 = self.energy(idx)
        e2 = part.energy(pidx)[mask]
        pt_part = 2 * self['pt', idx] * part['pt', pidx][mask]
        phi_part = pt_part * (np.cos(self['phi', idx] - part['phi', pidx][mask]))
        eta_part = pt_part * np.sinh(self['eta', idx]) * np.sinh(part['eta', pidx][mask])

        return np.sqrt(m1**2 + m2**2 + 2*e1*e2 - phi_part - eta_part)

