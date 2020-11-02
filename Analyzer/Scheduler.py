#!/usr/bin/env python3

import awkward1 as ak
import numpy as np
import threading
lock = threading.Lock()
from atomic import AtomicLong
import logging

from Analyzer import ApplyTask

class Scheduler:
    jobs = list()
    write_list = list()
    atomic = AtomicLong(0)
    
    def __init__(self, group, files, out_dir, xsec):
        self.task = ApplyTask(xsec, infile="{}/masks/{}.parquet".format(out_dir, group))
        self.group = group
        self.files = files
        self.out_dir = out_dir
        self.atomic += 1
        self.prevLine = "\033[{}F\033[K".format(self.atomic.value+1)
        self.nextLine = "\033[{}E ".format(self.atomic.value)

    def print_stat(self, string, end=False):
        text = string + '\x1b[0m'
        text = '\033[94m' + text if end else '\033[92m' + text
        lock.acquire()
        if logging.getLogger().level != logging.INFO:
            print(self.prevLine + text + self.nextLine)
        else:
            print(text)
        lock.release()

        
    def run(self):
        self.print_stat("{}: Starting Job".format(self.group))
        for job in Scheduler.jobs:
            cls = job(self.task)
            cls.run(self.files)
            self.task += cls
        self.print_stat("{}: Starting Write".format(self.group))
        self.task.write_out("{}/masks/{}.parquet".format(self.out_dir, self.group))
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
