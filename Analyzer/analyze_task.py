#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba
import time 
from anytree import Node, RenderTree
from collections import OrderedDict

from Analyzer import TaskHolder

class AnalyzeTask(TaskHolder):
    def __init__(self, task = None, redo=set(), *args, **kwargs):
        super().__init__(task=task)
        self.extraFuncs = list()
        self.tree_root = Node("base")
        self.redo = redo

    def add_job(self, func, outmask, invars=[], inmask=None, addvals=[]):
        inmask_dict = dict()
        if isinstance(inmask, str): inmask = [inmask]
        if isinstance(outmask, str): outmask = [outmask]
        if inmask is not None:
            for mask in inmask:
                particle = mask.split("_")[0] + "_"
                var_apply = [v for v in invars if particle in v]
                inmask_dict[mask] = var_apply
                for om in outmask:
                    self.dep_tree[om] = Node(om, self.dep_tree[mask])
        else:
            for om in outmask:
                self.dep_tree[om] = Node(om, self.tree_root)


        self.output.add(outmask) if isinstance(outmask, str) else self.output.update(outmask)
        addvals_dict = OrderedDict()
        for mask, additions in addvals:
            if isinstance(additions, str):
                addvals_dict[additions] = mask
            else:
                for add in additions:
                    addvals_dict[add] = mask
        self.extraFuncs.append((func, outmask, inmask_dict, invars, addvals_dict))

    def run(self, filename):
        start, end = 0, 0
        func_list = list()

        # for key, val in self.array_dict.items():
        #     print(key, ak.count_nonzero(val))
        # for pre, fill, node in RenderTree(self.tree_root):
        #     print("%s%s" % (pre, node.name))

        for func, write_name, inmask, var, addvals in self.extraFuncs:
            if self.do_run_job(write_name, inmask, addvals):
                self.redo.update(write_name)
                [self.array_dict.pop(name) for name in write_name if name in self.array_dict]
                func_list.append((func, write_name, inmask, var, addvals))
        allvars = self.get_all_vars(func_list)

        for array in uproot.iterate("{}:Events".format(filename), allvars):
            end += len(array)
            #print("Events considered: ", end)
            for func, write_name, inmask, var, addvals in func_list:
                events = array[var]
                for mask_name, vals in inmask.items():
                    submasks = self.get_masks(mask_name, start, end)
                    for submask in submasks:
                        for col in vals:
                            events[col] = events[col][self.array_dict[submask][start:end]]
                        
                for addval, mask in addvals.items():
                    events[addval] = self.add_var(mask, addval, start, end)

                time1 = time.time()
                self.apply_task(func, events, write_name, var+list(addvals.keys()))
                time2 = time.time()
                # print('\033[4m{:^20s}\033[0m function took {:.3f} ms ({:.0f} evt/s)'
                #       .format(func, (time2-time1)*1000.0,
                #               float("{:.2g}".format((end-start)/(time2-time1)))))
            start = end


    def do_run_job(self, write_name, inmask, addvals):
        exists = np.all([name in self.array_dict for name in write_name])
        redo = (np.any([i in self.redo for i in write_name]) or
                np.any([i in self.redo for i in inmask.keys()]) or
                np.any([i in self.redo for i in addvals.keys()]))

        return not exists or redo
            
    def get_all_vars(self, func_list):
        return_set = set()
        for _, _, _, var_list, _ in func_list:
            return_set |= set(var_list)
        return list(return_set)


    def get_masks(self, mask_name, start, end):
        apply_list = list()
        node = self.dep_tree[mask_name]
        while node.name != "base":
            apply_list.append(node.name)
            node = node.parent
        return apply_list[::-1]

    def add_var(self, mask_name, var_name, start, end):
        variable = self.array_dict[var_name][start:end]
        if mask_name is None:
            return variable
        var_parent = self.dep_tree[var_name].parent.name
        work_node = self.dep_tree[mask_name]
        apply_list = list()

        while work_node.name != var_parent:
            apply_list.append(work_node.name)
            work_node = work_node.parent

        for m_name in apply_list[::-1]:
            variable = variable[self.array_dict[m_name][start:end]]
        return variable

