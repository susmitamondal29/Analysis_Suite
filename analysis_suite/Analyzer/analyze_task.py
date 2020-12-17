#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba
import time 
from anytree import Node, RenderTree
from collections import OrderedDict
# from memory_profiler import profile
import itertools
import sys

from .task_holder import TaskHolder

class AnalyzeTask(TaskHolder):
    def __init__(self, redo=set(), *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                
        addvals_dict = OrderedDict()
        for mask, additions in addvals:
            if isinstance(additions, str):
                addvals_dict[additions] = mask
            else:
                for add in additions:
                    addvals_dict[add] = mask
        self.extraFuncs.append((func, outmask, inmask_dict, invars, addvals_dict))

    #@profile
    def run(self, filename, data_holder):
        start, end = 0, 0
        func_list = list()
        outputs = list()
        for func, write_name, inmask, var, addvals in self.extraFuncs:
            if self.do_run_job(write_name, inmask, addvals, data_holder.get_columns()):
                self.redo.update(write_name)
                outputs.extend(write_name)
                func_list.append((func, write_name, inmask, var, addvals))
        if not func_list:
            return False
        data_holder.setup_newvals(outputs)
        allvars = self.get_all_vars(func_list)

        print(filename)

        for array in uproot.iterate(f'{filename}:Events', allvars, step_size="300MB"):
            end += len(array)
            print("Events considered: ", start, end)
            for func, write_name, inmask, var, addvals in func_list:
                #print(func)
                events = array[var]
                for mask_name, vals in inmask.items():
                    submasks = self.get_masks(mask_name)
                    for submask, col in itertools.product(submasks, vals):
                        events[col] = events[col][data_holder.get_mask(submask, start, end)]

                for addval, mask in addvals.items():
                    mask_list = self.get_masks(mask, addval)
                    events[addval] = data_holder.get_variable(addval, start, end, mask_list)

                time1 = time.time()
                finished_mask = self.apply_task(func, events, var+list(addvals.keys()))
                data_holder.add_masks(finished_mask, write_name)
                time2 = time.time()

                print('\033[4m{:^20s}\033[0m function took {:.3f} ms ({:.0f} evt/s)'
                      .format(func, (time2-time1)*1000.0,
                              float("{:.2g}".format((end-start)/(time2-time1)))))
            start = end
        print("done")
        data_holder.end_run()
        return True

    def do_run_job(self, write_name, inmask, addvals, masks_that_exist):
        exists = np.all([name in masks_that_exist for name in write_name])
        redo = (np.any([i in self.redo for i in write_name]) or
                np.any([i in self.redo for i in inmask.keys()]) or
                np.any([i in self.redo for i in addvals.keys()]))
        
        return not exists or redo
            
    def get_all_vars(self, func_list):
        return_set = set()
        for _, _, _, var_list, _ in func_list:
            return_set |= set(var_list)
        return list(return_set)
                        
    def get_masks(self, mask_name, var_name=None):
        mask_list = list()
        if mask_name is None:
            return mask_list
        parent = "base" if var_name is None else self.dep_tree[var_name].parent.name
        work_node = self.dep_tree[mask_name]

        while work_node.name != parent:
            mask_list.append(work_node.name)
            work_node = work_node.parent
        return mask_list[::-1]
