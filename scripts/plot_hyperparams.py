#!/usr/bin/env python3
import numpy as np
import pandas as pd
import argparse
from pathlib import Path

from analysis_suite.commons.plot_utils import plot


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--workdir", required=True, type=lambda x : Path(x),
                    help="Working Directory")
args = parser.parse_args()


df = pd.read_csv(args.workdir / "minimize_results.csv")
variables = set(df.keys()) - {"AUC"}
fom = df["AUC"]

perc = 80
perc_start = (100-perc)/2
perc_end = (100+perc)/2

for var in variables:
    print(var)
    x_vals = df[var]


    x_dis = np.unique(x_vals)
    y_dis = [np.mean(fom[x_vals == x]) for x in x_dis]
    y_dis_median = [np.median(fom[x_vals == x]) for x in x_dis]
    y_dis_err = [np.std(fom[x_vals == x]) for x in x_dis]

    y_dis_pruned = list()
    y_dis_err_pruned = list()
    for x in x_dis:
        fom_vals = fom[x_vals==x]
        start, end = np.percentile(fom_vals, perc_start), np.percentile(fom_vals, perc_end)
        y_pruned = fom_vals[(fom_vals > start) & (fom_vals < end)]
        y_dis_pruned.append(np.mean(y_pruned))
        y_dis_err_pruned.append(np.std(y_pruned))


    with plot(args.workdir / f"{var}_hyper.png") as ax:
        ax.scatter(x_vals, fom)
        # plt.errorbar(x_dis, y_dis, yerr=y_dis_err, ecolor='r', capsize=10., color='r')
        ax.errorbar(x_dis, y_dis_pruned, yerr=y_dis_err_pruned, ecolor='g', capsize=10., color='g')
        ax.set_xlabel(var)
        if var == "min_child_weight":
            ax._setxscale("log")
