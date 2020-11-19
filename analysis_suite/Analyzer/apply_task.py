#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba

from .task_holder import TaskHolder


class ApplyTask(TaskHolder):
    sf_list = list()
    cut_list = list()
    var_list = list()
    der_var_list = list()
    make_list = list()
    
    def __init__(self, xsec, **kwargs):
        super().__init__(**kwargs)

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

    def initialize(self):
        cuts = list()
        subname = "|".join(["Event", "Jet", "Electron", "Muon"])
        regex = r'(({})\w+)'.format("|".join(ty))
        for cut_name in ApplyTask.cut_list:
            cut_name = re.sub(regex, r'self.array_dict["\1"]', cut_name)
            cuts.append(eval("ak.to_numpy({})".format(cut_name)))
        self.cuts = np.all(cuts, axis=0)

        base_scale = xsec/ak.sum(self.array_dict["Event_genScale"])
        self.output = {"scale_factor":
                       ak.Array([base_scale]*ak.count_nonzero(self.cuts))}
        for scale_name in ApplyTask.sf_list:
            self.output["scale_factor"] = (
                self.output["scale_factor"]* self.array_dict[scale_name][self.cuts])

        self.all_vars = set()
        for group, add_vars, _ in ApplyTask.var_list:
            for var in add_vars:
                self.output["{}/{}".format(group, var)] = ak.Array([])
            self.all_vars |= set(add_vars)

        for group, add_vars in ApplyTask.der_var_list:
            for var in add_vars:
                self.output["{}/{}".format(group, var)] = self.arrays[var][self.cuts]

        for group, add_vars, func, in_vars in ApplyTask.make_list:
            for var in add_vars:
                self.output["{}/{}".format(group, var)] = ak.Array([])
            self.all_vars |= set([i for v in in_vars for i in v[0]])

    def run(self, filename):
        allvars = list(self.all_vars)
        if len(allvars) == 0:
            return
        start, end = 0, 0
        for array in uproot.iterate("{}:Events".format(filename), allvars):
            end += len(array)
            mask = self.cuts[start:end]
            for group, add_vars, mask_name in ApplyTask.var_list:
                if mask_name is not None:
                    submask = self.array_dict[mask_name][start:end]
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

                    self.output[dict_name] = ak.concatenate(
                        [self.output[dict_name], var_arr])
            for group, add_vars, func, in_vars in ApplyTask.make_list:
                events = array[[i for v in in_vars for i in v[0]]]
                for var, mask_name in in_vars:
                    submask = self.array_dict[mask_name][start:end]
                    for v in var:
                        events[v] = events[v][submask]
                events = events[mask]
                add_vars = ["{}/{}".format(group, var) for var in add_vars]
                self.apply_task(func, events, add_vars)

            start = end


    @staticmethod
    @numba.jit(nopython=True)
    def unMask(events, builder):
        for event in events:
            builder.begin_list()
            for i in range(len(event)):
                builder.real(event[i])
            builder.end_list()
