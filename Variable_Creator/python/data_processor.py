#!/usr/bin/env python3
import pandas as pd
import logging
import uproot

from .vargetter import VarGetter
from analysis_suite.commons.info import fileInfo
from analysis_suite.commons.fake_rate_helper import get_dirnames, get_syst_index

class DataProcessor:
    def __init__(self, use_vars, lumi, systName="Nominal"):
        """Constructor method
        """
        self.systName = systName
        self.use_vars = use_vars
        self.all_vars = list(use_vars.keys()) + ["scale_factor"]
        self.lumi = lumi

    def get_final_dict(self, directory, tree):
        arr_dict = dict()
        root_files = directory.glob("*.root") if directory.is_dir() else [directory]
        print(tree)
        for root_file in root_files:
            members = get_dirnames(root_file)
            syst = get_syst_index(root_file, self.systName)
            for member in members:
                if "Signal" in tree and member == "data":
                    continue # blind SR
                xsec = fileInfo.get_xsec(member)*self.lumi if member != 'data' else 1
                vg = VarGetter(root_file, tree, member, xsec, syst)
                if not vg:
                    continue
                vg.setSyst(self.systName)
                vg.mergeParticles("TightLepton", "TightMuon", "TightElectron")
                arr_dict[member] = vg
        return arr_dict

    def process_year(self, infile, outdir, tree):
        # Process input file
        vg_dict = self.get_final_dict(infile, tree)
        final_set = dict()

        for member, vg in vg_dict.items():
            if not len(vg):
                logging.warning(f'Sample {member} has no events in it!')
                continue
            df_dict = {varname: func(vg) for varname, func in self.use_vars.items()}
            df_dict["scale_factor"] = vg.scale
            df = pd.DataFrame.from_dict(df_dict)
            final_set[member] = df.astype({col: int for col in df.columns if col[0] == 'N'})
            print(f"Finished setting up {member}")
        self._write_out(outdir / f'processed_{self.systName}_{tree}.root', final_set)

    def _write_out(self, outfile, workSet):
        """**Write out pandas file as a compressed pickle file

        Args:
          outfile(string): Name of file to write
          workSet(pandas.DataFrame): DataFrame of variables to write out
          prediction(pandas.DataFrame): DataFrame of BDT predictions

        """
        with uproot.recreate(outfile) as f:
            for group, df in workSet.items():
                if not len(df):
                    continue
                f[group] = df
