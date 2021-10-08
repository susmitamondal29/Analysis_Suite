#!/usr/bin/env python3
import skopt
from collections import OrderedDict
import numpy as np
import pprint
import csv

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import get_cli, getGroupDict
import analysis_suite.data.inputs as mva_params
from analysis_suite.BDT_utilities.job_main import get_mva_runner

import sys
sys.argv.insert(1, "mva")


nVars = len(mva_params.usevars)
hyperParams = OrderedDict({
    "hidden_layers": np.array([1, 2]),
    "initial_nodes": np.array([nVars, nVars + 1]),
    "node_pattern": np.array(["static", "dynamic"]),
    "batch_power": np.array([8, 11]),
    "learning_rate": np.array([0.001, 0.005, 0.01, 0.05]),
    "regulator": np.array(["dropout", "none"]),
    "activation": np.array(["softplus", "elu"]),
    "epochs": np.array([1, 3]),
})


def write_line(filename, params, auc):
    with open(filename, "a") as logfile:
        writer = csv.writer(logfile)
        writer.writerow(params + [auc])


# Determine optimization space
def create_opt_space(params):
    opt_space = []
    for key, vals in params.items():
        if vals.dtype.type is np.str_ or len(vals) != 2:
            opt_space.append(skopt.space.Categorical(vals, name=key))
        else:
            opt_space.append(skopt.space.Integer(*vals, name=key))
    return opt_space


# Objective function
def run_mva(mvaRunner, **X):
    print("\n>> Configuration:")
    print(X)

    params = X.update(extraOptions)
    mvaRunner.update_params(X)
    mvaRunner.train(cli_args.workdir)
    mvaRunner.apply_model(cli_args.workdir, "2016")
    fom = mvaRunner.fom["2016"]
    auc = mvaRunner.auc["2016"]

    print(f"\n>> Obtained ROC-Integral value: {auc}")
    print(f">> Obtained FOM value: {fom}")
    write_line(logfile_name, [X[i] for i in pNames], fom)

    return -fom


if __name__ == "__main__":
    # user parameters
    cli_args = get_cli()
    work_year = "2016"
    extraOptions = {"verbose": False}
    number_calls = 3

    # Derived Variables
    pNames = list(hyperParams.keys())
    logfile_name = cli_args.workdir / "minimize_results.csv"
    hyper_file = cli_args.workdir / "hyperParams.py"
    group_info = GroupInfo(analysis=cli_args.analysis)
    groupDict = getGroupDict(mva_params.groups, group_info)
    opt_space = create_opt_space(hyperParams)

    # Save used parameters to file
    with open( hyper_file, "w" ) as f:
        varName = "hyperParams="
        f.write(varName)
        f.write(pprint.pformat(hyperParams, indent=len(varName)))
        f.write("\n")
        print( "[OK ] Parameters saved to dataset folder." )

    # Start the logfile
    with open(logfile_name,'w') as f: pass # clear file
    write_line(logfile_name, list(hyperParams), "AUC")

    # Setup mva
    mvaRunner = get_mva_runner(cli_args.train)(mva_params.usevars, groupDict)
    for year in cli_args.years:
        mvaRunner.setup_year(cli_args.workdir, year)

    # Perform the optimization
    @skopt.utils.use_named_args(opt_space)
    def objective(**X):
        return run_mva(mvaRunner, **X)

    res_gp = skopt.gp_minimize(
        func = objective,
        dimensions = opt_space,
        n_calls = number_calls,
        n_random_starts = number_calls,
        verbose = True
    )

    # Report results
    with open(hyper_name, "a") as f:
        result = {key: res_gp.x[i] for i, key in enumerate(pNames)}
        print("TTT DNN Hyper Parameter Optimization Parameters")
        print(f"Static and Parameter Space stored in: {config_file}")
        print("Optimized Parameters:")
        for key, val in result.items():
            print(f"    {key}: {val}")

        varName = "best_params="
        config.write(varName)
        config.write(pprint.pformat(result, indent=len(varName)))
        config.write("\n")
