#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba
import time 
from anytree import Node
from collections import OrderedDict

from Analyzer import TaskHolder

class AnalyzeTask(TaskHolder):
    def __init__(self, task = None, *args):
        super().__init__(task=task)

        self.mask_tree = dict()
        self.extraFuncs = list()
        if isinstance(task, AnalyzeTask):
            self.mask_tree = task.mask_tree

    def __iadd__(self, other):
        if isinstance(other, TaskHolder):
            self.mask_tree.update(other.mask_tree)
        return super().__iadd__(other)


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
                    self.mask_tree[om] = Node(om, self.mask_tree[mask])
        else:
            for om in outmask:
                self.mask_tree[om] = Node(om, Node("base"))


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
        allvars = self.get_all_vars()
        start, end = 0, 0
        for array in uproot.iterate("{}:Events".format(filename), allvars):
            end += len(array)
            print("Events considered: ", end)
            for func, write_name, inmask, var, addvals in self.extraFuncs:
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
                print('\033[4m{:s}\033[0m function took {:.3f} ms ({:d} evt/s)'.format(func, (time2-time1)*1000.0, int((end-start)/(time2-time1))))
            start = end

            
    def get_all_vars(self):
        return_set = set()
        for _, _, _, var_list, _ in self.extraFuncs:
            return_set |= set(var_list)
        return list(return_set)


    def get_masks(self, mask_name, start, end):
        apply_list = list()
        node = self.mask_tree[mask_name]
        while node.name != "base":
            apply_list.append(node.name)
            node = node.parent
        return apply_list[::-1]

    def add_var(self, mask_name, var_name, start, end):
        variable = self.array_dict[var_name][start:end]
        if mask_name is None:
            return variable
        var_parent = self.mask_tree[var_name].parent.name
        work_node = self.mask_tree[mask_name]
        apply_list = list()

        while work_node.name != var_parent:
            apply_list.append(work_node.name)
            work_node = work_node.parent

        for m_name in apply_list[::-1]:
            variable = variable[self.array_dict[m_name][start:end]]
        return variable

