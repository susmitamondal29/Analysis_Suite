#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba
import re

from .task_holder import TaskHolder


class ApplyTask(TaskHolder):
    sf_list = list()
    cut_list = list()
    var_list = list()
    der_var_list = list()
    make_list = list()
    
    def __init__(self, xsec, **kwargs):
        super().__init__(**kwargs)
        self.xsec = xsec
        self.all_vars = set()
        
    @staticmethod
    def add_scale_factor(scale_name):
        ApplyTask.sf_list.append(scale_name)

    @staticmethod
    def add_cut(cut_name):
        ApplyTask.cut_list.append(cut_name)

    @staticmethod
    def add_vars(groupName, var_list, mask=None):
        ApplyTask.var_list.append((groupName, var_list, mask))

    @staticmethod
    def add_derived_vars(groupName, var_list):
        ApplyTask.der_var_list.append((groupName, var_list))

    @staticmethod
    def add_make_vars(groupName, add_vars, func, *args):
        ApplyTask.make_list.append((groupName, add_vars, func, args))

    def setup_variables(self, indata, outdata):
        ## Setup basic cuts
        cut_list = list()
        subname = "|".join(["Event", "Jet", "Electron", "Muon"])
        regex = r'(({})\w+)'.format(subname)
        for cut_name in ApplyTask.cut_list:
            cut_name = re.sub(regex, r'indata.get_mask("\1")', cut_name)
            cut_list.append(eval("ak.to_numpy({})".format(cut_name)))
        self.cuts = np.all(cut_list, axis=0)

        ## setup basic scale factor
        base_scale = self.xsec/ak.sum(indata.get_mask("Event_genScale"))
        scale_factor = ak.Array([base_scale]*ak.count_nonzero(self.cuts))
        for scale_name in ApplyTask.sf_list:
            scale_factor = (scale_factor * indata.get_mask(scale_name)[self.cuts])
        outdata.immediate_add("scale_factor", scale_factor)

        ## variables to be filled immediately
        for group, add_vars in ApplyTask.der_var_list:
            for var in add_vars:
                outdata.immediate_add("{}/{}".format(group, var), indata.get_mask(var)[self.cuts])
 
        # variables TO be filled
        for group, add_vars, _ in ApplyTask.var_list:
            outdata.setup_newvals(["{}/{}".format(group, var) for var in add_vars])
            self.all_vars |= set(add_vars)

        for group, add_vars, func, in_vars in ApplyTask.make_list:
            outdata.setup_newvals(["{}/{}".format(group, var) for var in add_vars])
            self.all_vars |= set([i for v in in_vars for i in v[0]])


    def run(self, filename, indata, outdata):
        self.setup_variables(indata, outdata)
        
        allvars = list(self.all_vars)
        if len(allvars) == 0:
            return
        
        start, end = 0, 0
        for array in uproot.iterate("{}:Events".format(filename), allvars):
            end += len(array)
            mask = self.cuts[start:end]
            for group, add_vars, mask_name in ApplyTask.var_list:
                if mask_name is not None:
                    submask = indata.get_variable(mask_name, start, end)
                    subarray = array[add_vars][submask]
                    subarray = subarray[mask]
                else:
                    subarray = array[add_vars][mask]

                for var in add_vars:
                    dict_name = "{}/{}".format(group, var)
                    if "var" in repr(ak.type(subarray[var])):
                        awk_var = ak.ArrayBuilder()
                        ApplyTask.unMask(subarray[var], awk_var)
                        var_arr = awk_var.snapshot()
                    else:
                        var_arr = subarray[var]

                    outdata.add_masks(var_arr, dict_name)
            for group, add_vars, func, in_vars in ApplyTask.make_list:
                events = array[[i for v in in_vars for i in v[0]]]
                for var, mask_name in in_vars:
                    submask = indata.get_variable(mask_name, start, end)
                    for v in var:
                        events[v] = events[v][submask]
                events = events[mask]
                add_vars = ["{}/{}".format(group, var) for var in add_vars]
                finished_mask = self.apply_task(func, events, add_vars)
                outdata.add_masks(finished_mask, add_vars)
            start = end
        outdata.end_run()

    @staticmethod
    @numba.jit(nopython=True)
    def unMask(events, builder):
        for event in events:
            builder.begin_list()
            for i in range(len(event)):
                builder.real(event[i])
            builder.end_list()

    @staticmethod
    @numba.jit(nopython=True)
    def merge_leptons(events, builder):
        for event in events:
            builder.begin_list()
            midx, eidx = 0, 0
            for _ in range(len(event.Muon_pt) +len(event.Electron_pt)):
                builder.begin_tuple(4)
                if (midx != len(event.Muon_pt) and
                    (eidx == len(event.Electron_pt) or
                     event.Muon_pt[midx] > event.Electron_pt[eidx])):
                    builder.index(0).real(event.Muon_pt[midx])
                    builder.index(1).real(event.Muon_eta[midx])
                    builder.index(2).real(event.Muon_phi[midx])
                    builder.index(3).integer(event.Muon_charge[midx]*13)
                    midx += 1
                else:
                    builder.index(0).real(event.Electron_pt[eidx])
                    builder.index(1).real(event.Electron_eta[eidx])
                    builder.index(2).real(event.Electron_phi[eidx])
                    builder.index(3).integer(event.Electron_charge[eidx]*11)
                    eidx += 1
                builder.end_tuple()
            builder.end_list()
