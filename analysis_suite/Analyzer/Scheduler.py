#!/usr/bin/env python3

import awkward1 as ak
import numpy as np
import threading
lock = threading.Lock()
from atomic import AtomicLong
import logging
import os
#from memory_profiler import profile

from .task_holder import DataHolder
from .apply_task import ApplyTask

class Scheduler:
    jobs = list()
    write_list = list()
    atomic = AtomicLong(0)

    #@profile
    def __init__(self, group, files, out_dir, xsec):
        self.data = DataHolder(infile="{}/masks/{}.parquet".format(out_dir, group))
        self.xsec = xsec
        self.group = group
        self.files = files
        self.out_dir = out_dir
        self.atomic += 1
        self.prevLine = "\033[{}F\033[K".format(self.atomic.value+1)
        self.nextLine = "\033[{}E ".format(self.atomic.value)


    def print_stat(self, string, end=False):
        text = string + '\x1b[0m'
        text = '\033[94m' + text if end else '\033[92m' + text
        # lock.acquire()
        # if logging.getLogger().level != logging.INFO:
        #     print(self.prevLine + text + self.nextLine)
        # else:
        print(text)
        # lock.release()

    # @profile
    def run(self, redo):
        self.print_stat("{}: Starting Job".format(self.group))
        need_to_save = False
        depTree = dict()
        for job in Scheduler.jobs:
            cls = job(redo=redo, dep_tree=depTree)
            jobsave = cls.run(self.files, self.data)
            need_to_save = need_to_save or jobsave
            redo.update(cls.redo)
            depTree = cls.dep_tree
            
        if self.out_dir == ".":
            self.data.write_out("{}.parquet".format(self.group))
        else:
            self.data.write_out("{}/{}.parquet".format(self.out_dir, self.group))
        self.print_stat("{}: Finished Write".format(self.group), end=True)

    def apply_mask(self, chan):
        pass
        # self.print_stat("{}: Starting Apply".format(self.group))
        # cut_apply = CutApplier(ak.from_parquet(
        #     "{}/masks/{}.parquet".format(self.out_dir, self.group)), self.xsec)
        # cut_apply.run(self.files)

        # # write
        # self.print_stat("{}: Starting Write".format(self.group))

        # total_mask = ak.Array({})
        # for key, arr in cut_apply.output.items():
        #     total_mask[key] = arr
        # ak.to_parquet(total_mask, "{}/{}/{}.parquet"
        #               .format(self.out_dir, chan, self.group),
        #               compression="gzip")
        # self.print_stat("{}: Finished Write".format(self.group), end=True)
