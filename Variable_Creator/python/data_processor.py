#!/usr/bin/env python3
from collections import OrderedDict
import numpy as np
import pandas as pd
import logging
from .vargetter import VarGetter
import awkward1 as ak
from pathlib import Path
import uproot4
import uproot as upwrite

class DataProcessor:
    def __init__(self, use_vars, systName="Nominal"):
        """Constructor method
        """
        self.systName = systName
        self.use_vars = use_vars
        self.all_vars = list(use_vars.keys()) + ["scale_factor"]

    def get_final_dict(self, directory, tree):
        arr_dict = dict()
        path = Path(directory)
        root_files = path.rglob("*.root") if path.is_dir() else [path]
        for root_file in root_files:
            groups = list()
            syst = 0
            with uproot4.open(root_file) as f:
                groups = [key.strip(";1") for key in f.keys() if "/" not in key]
                systNames = [systName.member("fName") for systName in f[groups[0]]["Systematics"]]
                systNames = list(OrderedDict.fromkeys(systNames))
                syst = systNames.index(self.systName)
                for group in groups:
                    if group not in arr_dict:
                        arr_dict[group] = VarGetter(f, tree, group, syst)
                    else:
                        arr_dict[group] += VarGetter(f, tree, group, syst)
        for key, val in arr_dict.items():
            val.set_JEC(self.systName)

        return arr_dict

    def process_year(self, infile, outdir, tree):
        # Process input file
        arr_dict = self.get_final_dict(infile, tree)
        final_set = dict()

        for sample, arr in arr_dict.items():
            if not len(arr):
                logging.warning(f'Sample {sample} has no events in it!')
                continue
            df_dict = {varname: func.apply(arr) for varname, func in self.use_vars.items()}
            df_dict["scale_factor"] = ak.to_numpy(arr.scale)
            df = pd.DataFrame.from_dict(df_dict)
            final_set[sample] = df

        treename = "" if tree == "Analyzed" else f'_{tree}'
        self._write_out(outdir / f'processed_{self.systName}{treename}.root', final_set)

    def _write_out(self, outfile, workSet):
        """**Write out pandas file as a compressed pickle file

        Args:
          outfile(string): Name of file to write
          workSet(pandas.DataFrame): DataFrame of variables to write out
          prediction(pandas.DataFrame): DataFrame of BDT predictions

        """
        branches = {key: np.int32 if key[0] == "N" else  np.float32 for key in self.all_vars}
        with upwrite.recreate(outfile) as f:
            for group, df in workSet.items():
                if not len(df):
                    continue
                f[group] = upwrite.newtree(branches)
                f[group].extend(df.to_dict('list'))
