#!/usr/bin/env python3

import awkward1 as ak
from os.path import isfile

class TaskHolder():
    def __init__(self, **kwargs):
        if "task" in kwargs:
            self.array_dict = kwargs["task"].array_dict
        elif "infile" in kwargs and isfile(kwargs["infile"]):
            arrays = ak.from_parquet(kwargs["infile"])
            self.array_dict = {key: arrays[key] for key in arrays.columns}
        else:
            self.array_dict = dict()
        self.output = set()


    def __iadd__(self, other):
        if isinstance(other, TaskHolder):
            self.array_dict.update({var: other.array_dict[var] for var in other.output})
        else:
            self.array_dict.update({col: other[col] for col in other.columns})
        return self

    def apply_task(self, func, events, add_vars, variables=None):
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

 
        if isinstance(final_build, tuple):
            for var, var_arr in zip(add_vars, final_build):
                if var not in self.array_dict:
                    self.array_dict[var] = var_arr
                else:
                    self.array_dict[var] = ak.concatenate([self.array_dict[var], var_arr])
        else:
            var = add_vars[0]
            if var not in self.array_dict:
                self.array_dict[var] = final_build
            else:
                self.array_dict[var] = ak.concatenate([self.array_dict[var], final_build])



    def isJit(self, funcName):
        return "Dispatcher" in repr(getattr(self, funcName))

    def isVectorize(self, funcName):
        return "DUFunc" in repr(getattr(self, funcName))

    def write_out(self, outname):
        output = self.output if self.output else self.array_dict.keys()
        total_mask = ak.Array({})
        for key in output:
            total_mask[key] = self.array_dict[key]
        ak.to_parquet(total_mask, outname, compression="gzip")
