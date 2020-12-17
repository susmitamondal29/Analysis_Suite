#!/usr/bin/env python3
import awkward1 as ak
from os.path import isfile
import bz2
import pickle
import _pickle as cPickle
#from memory_profiler import profile

class TaskHolder():
    #@profile
    def __init__(self, *args, **kwargs):
        self.dep_tree = dict()
        if "dep_tree" in kwargs:
            self.dep_tree.update(kwargs["dep_tree"])
        self.output = set()

    def apply_task(self, func, events, variables=None):
        final_build = None
        if self.isJit(func):
            builder = ak.ArrayBuilder()
            getattr(self, func)(events, builder)
            final_build = ak.unzip(builder.snapshot())
        elif self.isVectorize(func):
            variables = [events[col] for col in variables]
            # print([ak.type(v[0]) for v in variables])
            final_build = ak.unzip(getattr(self, func)(*variables))
        else:
            final_build = ak.unzip(getattr(self, func)(events))
            
        return final_build
        
    def isJit(self, funcName):
        return "Dispatcher" in repr(getattr(self, funcName))

    def isVectorize(self, funcName):
        return ("DUFunc" in repr(getattr(self, funcName)) or
           "ufunc" in repr(getattr(self, funcName)))


class DataHolder:
    def __init__(self, infile):
        if isfile(infile):
            self.old_vals = self.read_in(infile)
        else:
            self.old_vals = ak.Array({})
        self.old_names = self.old_vals.columns
        self.new_vals = dict()
        
    def setup_newvals(self, names):
        for name in names:
            self.new_vals[name] = ak.Array([])

    def get_mask(self, name, start=None, stop=None):
        if name in self.old_names:
            return self.old_vals[name][start:stop]
        else:
            return self.new_vals[name][start:stop]

    def get_columns(self):
        return self.old_names

    def get_variable(self, name, start=None, stop=None, mask_list=list()):
        variable = self.get_mask(name, start, stop)
        for m_name in mask_list:
            variable = variable[self.get_mask(m_name, start, stop)]
        return variable

    def add_masks(self, build, add_vars):
        if isinstance(add_vars, list):
            for i, var in enumerate(add_vars):
                self.new_vals[var] = ak.concatenate((self.new_vals[var], build[i]))
        else:
            self.new_vals[add_vars] = ak.concatenate((self.new_vals[add_vars], build))

    def immediate_add(self, varname, var):
        self.old_names.append(varname)
        self.old_vals[varname] = var

    def end_run(self):
        for col in self.new_vals.keys():
            self.old_vals[col] = self.new_vals[col]
        self.old_names = self.old_vals.columns
        self.new_vals = dict()

    def write_out(self, outname):
        with bz2.BZ2File(outname, 'w') as f:
            cPickle.dump(self.old_vals, f)

    def read_in(self, inname):
         return cPickle.load(bz2.BZ2File(inname, 'rb'))
