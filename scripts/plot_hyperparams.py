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
variables = set(df.keys()) - {"FOM"}
fom = df["FOM"]

for var in variables:
    print(var)
    x_vals = df[var]
    x_dis = np.unique(x_vals)
    y_dis_mean = [np.mean(fom[x_vals == x]) for x in x_dis]
    y_dis_median = [np.median(fom[x_vals == x]) for x in x_dis]
    y_dis_err = [np.std(fom[x_vals == x]) for x in x_dis]

    y_dis_pruned = list()
    y_dis_err_pruned = list()
    for x in x_dis:
        y_for_val = sorted(fom[x_vals==x])
        y_dis_pruned.append(np.mean(y_for_val[1:-1]))
        y_dis_err_pruned.append(np.std(y_for_val[1:-1]))

    with plot(args.workdir / f"{var}_hyper.png") as ax:
        ax.scatter(x_vals, fom)
        ax.errorbar(x_dis, y_dis_mean, yerr=y_dis_err, ecolor='r', capsize=10., color='r')
        # plt.errorbar(x_dis, y_dis_pruned, yerr=y_dis_err_pruned, ecolor='r', capsize=10., color='r')
        ax.set_xlabel(var)
        if var == "min_child_weight":
            plt.xscale("log")
