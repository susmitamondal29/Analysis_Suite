#!/usr/bin/env python3
from .Process import Process
from .CutApplier import CutApplier
import awkward1 as ak
import numpy as np

import threading
lock = threading.Lock()
from atomic import AtomicLong

class Scheduler:
    jobs = list()
    write_list = list()
    atomic = AtomicLong(0)
    
    def __init__(self, group, files, out_dir, xsec):
        self.process = Process()
        self.group = group
        self.files = files
        self.out_dir = out_dir
        self.xsec = xsec
        self.atomic += 1
        self.prevLine = "\033[{}F\033[K".format(self.atomic.value+1)
        self.nextLine = "\033[{}E ".format(self.atomic.value)

    @staticmethod
    def add_step(class_list):
        Scheduler.jobs.append(class_list)


    def print_stat(self, string, end=False):
        text = string + '\x1b[0m'
        text = '\033[94m' + text if end else '\033[92m' + text
        lock.acquire()
        print(self.prevLine + text + self.nextLine)
        lock.release()

        
    def run(self):
        self.print_stat("{}: Starting Job".format(self.group))

        for job in Scheduler.jobs:
            classes = [cls(self.process) for cls in job]
            for cls in classes:
                cls.run(self.files)
                self.process += cls
        self.print_stat("{}: Finished Job".format(self.group), end=True)

        
    def add_tree(self):
        self.print_stat("{}: Starting Write".format(self.group))
        total_mask = ak.Array({})
        for key, arr in self.process.outmasks.items():
            total_mask[key] = arr
        ak.to_parquet(total_mask, "{}/{}.parquet".format(self.out_dir, self.group),
                      compression="gzip")
        self.print_stat("{}: Finished Write".format(self.group), end=True)

    def apply_mask(self, chan):
        self.print_stat("{}: Starting Apply".format(self.group))
        cut_apply = CutApplier(ak.from_parquet(
            "{}/{}.parquet".format(self.out_dir, self.group)), self.xsec)
        cut_apply.run(self.files)

        # write
        self.print_stat("{}: Starting Write".format(self.group))
        total_mask = ak.Array({})
        for key, arr in cut_apply.output.items():
            total_mask[key] = arr
        ak.to_parquet(total_mask, "{}/{}/{}.parquet"
                      .format(self.out_dir, chan, self.group),
                      compression="gzip")
        self.print_stat("{}: Finished Write".format(self.group), end=True)
