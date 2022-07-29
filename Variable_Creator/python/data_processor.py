#!/usr/bin/env python3
import pandas as pd
import logging
import uproot

from .vargetter import VarGetter
from analysis_suite.commons.info import fileInfo
from analysis_suite.commons.configs import get_dirnames, get_syst_index
import analysis_suite.data.inputs as mva_params

class DataProcessor:
    def __init__(self, use_vars, lumi, systName="Nominal", cut=None):
        """Constructor method
        """
        self.systName = systName
        self.use_vars = use_vars
        self.all_vars = list(use_vars.keys()) + ["scale_factor"]
        self.lumi = lumi
        self.final_set = dict()
        self.cut = cut

    def __bool__(self):
        return bool(self.final_set)


    def get_final_dict(self, directory, tree):
        arr_dict = dict()
        root_files = directory.glob("*.root") if directory.is_dir() else [directory]
        for root_file in root_files:
            members = get_dirnames(root_file)
            syst = get_syst_index(root_file, self.systName)
            if syst == -1:
                continue
            for member in members:
                if "Signal" in tree and member == "data":
                    continue # blind SR
                xsec = fileInfo.get_xsec(member)*self.lumi*1000 if member != 'data' else 1
                vg = VarGetter(root_file, tree, member, xsec, syst)
                if not vg:
                    continue

                self.apply_cuts(vg)
                vg.setSyst(self.systName)
                vg.mergeParticles("TightLepton", "TightMuon", "TightElectron")
                if tree in mva_params.change_name:
                    member = mva_params.change_name[tree]
                arr_dict[member] = vg
        return arr_dict

    def process_year(self, infile, tree):
        # Process input file
        vg_dict = self.get_final_dict(infile, tree)

        for member, vg in vg_dict.items():
            if not len(vg):
                logging.warning(f'Sample {member} has no events in it!')
                continue
            df_dict = {varname: func(vg) for varname, func in self.use_vars.items()}
            df_dict["scale_factor"] = vg.scale
            df = pd.DataFrame.from_dict(df_dict)
            df = df.astype({col: int for col in df.columns if col[0] == 'N'})
            if member not in self.final_set:
                self.final_set[member] = df
            else:
                self.final_set[member] = pd.concat([self.final_set[member], df], ignore_index=True)
            print(f"Finished setting up {member} in tree {tree}")

    def apply_cuts(self, vg):
        if self.cut is None:
            pass
        else:
            vg.mask = self.cut(vg)

    def write_out(self, outfile):
        """**Write out pandas file as a compressed pickle file

        Args:
          outfile(string): Name of file to write
          workSet(pandas.DataFrame): DataFrame of variables to write out
          prediction(pandas.DataFrame): DataFrame of BDT predictions

        """
        with uproot.recreate(outfile) as f:
            for group, df in self.final_set.items():
                if not len(df):
                    continue
                f[group] = df
