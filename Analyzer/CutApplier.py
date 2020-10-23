#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba

import Analyzer.Common

class CutApplier:
    sf_list = list()
    cut_list = list()
    var_list = list()
    der_var_list = list()
    make_list = list()
    def __init__(self, arrays, xsec):
        self.arrays = arrays
        self.cuts = np.ones(len(arrays), dtype=bool)
        self.all_vars = set()
        scale = xsec/ak.sum(arrays.Event_genScale)
        
        cuts = list()
        for cut_name in CutApplier.cut_list:
            for rep in ["Event", "Jet", "Electron", "Muon"]:
                cut_name = cut_name.replace(rep, "arrays."+rep)
            cuts.append(eval("ak.to_numpy({})".format(cut_name)))
        self.cuts = np.all(cuts, axis=0)
        
        self.output = dict()
        self.output = {"scale_factor": ak.Array([scale]*len(arrays[self.cuts]))}
        for scale_name in CutApplier.sf_list:
            self.output["scale_factor"] = (self.output["scale_factor"]
                                           * arrays[scale_name][self.cuts])
        for group, add_vars, _ in CutApplier.var_list:
            for var in add_vars:
                self.output["{}/{}".format(group, var)] = ak.Array([])
            self.all_vars |= set(add_vars)
            
        for group, add_vars in CutApplier.der_var_list:
            for var in add_vars:
                self.output["{}/{}".format(group, var)] = self.arrays[var][self.cuts]

        for group, add_vars, func, in_vars in CutApplier.make_list:
            for var in add_vars:
                self.output["{}/{}".format(group, var)] = ak.Array([])
            self.all_vars |= set([i for v in in_vars for i in v[0]])
        
    @staticmethod
    def add_scale_factor(scale_name):
        CutApplier.sf_list.append(scale_name)

    @staticmethod
    def add_cut(cut_name):
        CutApplier.cut_list.append(cut_name)

    @staticmethod
    def add_vars(groupName, var_list, mask=None):
        CutApplier.var_list.append((groupName, var_list, mask))

    @staticmethod
    def add_vars_derived(groupName, var_list):
        CutApplier.der_var_list.append((groupName, var_list))

    @staticmethod
    def add_make_vars(groupName, add_vars, func, *args):
        CutApplier.make_list.append((groupName, add_vars, func, args))

    def run(self, filename):
        allvars = list(self.all_vars)
        if len(allvars) == 0:
            return
        start, end = 0, 0
        for array in uproot.iterate("{}:Events".format(filename), allvars):
            end += len(array)
            mask = self.cuts[start:end]
            for group, add_vars, mask_name in CutApplier.var_list:
                if mask_name is not None:
                    submask = self.arrays[mask_name][start:end]
                    subarray = array[add_vars][submask]
                    subarray = subarray[mask]
                else:
                    subarray = array[add_vars][mask]
                    
                for var in add_vars:
                    dict_name = "{}/{}".format(group, var)
                    if "var" in repr(ak.type(subarray[var])):
                        awk_var = ak.ArrayBuilder()
                        CutApplier.unMask(subarray[var], awk_var)
                        var_arr = awk_var.snapshot()
                    else:
                        var_arr = subarray[var]
                        
                    self.output[dict_name] = ak.concatenate(
                        [self.output[dict_name], var_arr])
            for group, add_vars, func, in_vars in CutApplier.make_list:
                events = array[[i for v in in_vars for i in v[0]]]
                for var, mask_name in in_vars:
                    submask = self.arrays[mask_name][start:end]
                    for v in var:
                        events[v] = events[v][submask]
                events = events[mask]

                builder = ak.ArrayBuilder()
                getattr(Analyzer.Common, func)(events, builder)
                final_build = ak.unzip(builder.snapshot())
                
                for var, var_arr in zip(add_vars, final_build):
                    dict_name = "{}/{}".format(group, var)
                    self.output[dict_name] = ak.concatenate(
                        [self.output[dict_name], var_arr])
            start = end

    @staticmethod
    @numba.jit(nopython=True)
    def unMask(events, builder):
        for event in events:
            builder.begin_list()
            for i in range(len(event)):
                builder.real(event[i])
            builder.end_list()
