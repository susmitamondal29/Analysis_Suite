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
        self.xsec = xsec
        self.group = group
        self.files = files
        self.atomic += 1
        self.prevLine = "\033[{}F\033[K".format(self.atomic.value+1)
        self.nextLine = "\033[{}E ".format(self.atomic.value)
        if out_dir == ".":
            self.pq_filename = "{}.pbz2".format(self.group)
            self.analyzed_filename = "analyzed_{}.pbz2".format(self.group)
        else:
            self.pq_filename = "{}/{}.pbz2".format(out_dir, self.group)
            self.analyzed_filename = "{}/{}/{}.pbz2".format(self.out_dir, chan, self.group)
            
        self.data = DataHolder(infile=self.pq_filename)

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
        if need_to_save:
            self.data.write_out(self.pq_filename)
        self.print_stat("{}: Finished Write".format(self.group), end=True)

    def apply_mask(self, chan):
        self.print_stat("{}: Starting Apply".format(self.group))
        print(self.data.get_columns())
        self.proc_data = DataHolder(infile="proc_data.pbz2")
        cut_apply = ApplyTask(self.xsec)
        cut_apply.run(self.files, self.data, self.proc_data)

        # write
        self.print_stat("{}: Starting Write".format(self.group))
        self.proc_data.write_out(self.analyzed_filename)

        self.print_stat("{}: Finished Write".format(self.group), end=True)
