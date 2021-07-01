#!/usr/bin/env python3
import skopt
import math
from collections import OrderedDict
import numpy as np
import pprint

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir, getGroupDict
import analysis_suite.data.inputs as mva_params
from analysis_suite.BDT_utilities.DNN import KerasMaker

# user parameters
workdir = "test_workdir"
extraOptions = {"verbose": True}
number_calls = 3

nVars = len(mva_params.usevar)
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


logfile_name = f"{workdir}/minimize_results.log"
config_file = f"{workdir}/config.json"
group_info = GroupInfo(analysis="ThreeTop")
groupDict = getGroupDict(mva_params.groups, group_info)

# Save used parameters to file
with open( config_file, "w" ) as f:
    f.write(pprint.pformat(hyperParams))
    print( "[OK ] Parameters saved to dataset folder." )

# clear file
with open(logfile_name,'w') as f: pass

def write_line(filename, params, auc):
    with open(filename, "a") as logfile:
        logfile.write("| ")
        logfile.write(" | ".join(params))
        logfile.write(f" | {auc} |\n")


# Start the logfile
write_line(logfile_name, list(hyperParams), "AUC")

# Determine optimization space
opt_space = []
for key, vals in hyperParams.items():
    if vals.dtype.type is np.str_ or len(vals) != 2:
        opt_space.append(skopt.space.Categorical(vals, name=key))
    else:
        opt_space.append(skopt.space.Integer(*vals, name=key))
opt_order = list(hyperParams.keys())
    


# Objective function
@skopt.utils.use_named_args(opt_space)
def objective(**X):
    print("\n>> Configuration:")
    print(f"{X}")

    params = X.update(extraOptions)
    mvaRunner = KerasMaker(mva_params.usevar, groupDict, params=X)
    mvaRunner.setup_files(workdir, train=True)
    mvaRunner.train(workdir)

    print(f"\n>> Obtained ROC-Integral value: {mvaRunner.auc_test}")
    with open(logfile_name, "a" ) as logfile:
        logfile.write("| ")
        logfile.write(" | ".join([str(X[keys]) for keys in hyperParams.keys()]))
        logfile.write(f" | {mvaRunner.auc_train:.3f} |\n")
        
    opt_metric = math.log(1 - mvaRunner.auc_test)
    print( f"\n>> Metric: {opt_metric:.4f}")
    return opt_metric


# Perform the optimization
res_gp = skopt.gp_minimize(
    func = objective,
    dimensions = opt_space,
    n_calls = number_calls,
    n_random_starts = number_calls,
    verbose = True
)

# Report results
with open(logfile_name, "a") as logfile:
    logfile.write("TTT DNN Hyper Parameter Optimization Parameters \n")
    # f.write("Static and Parameter Space stored in: {}\n".format(config_file))
    logfile.write("Optimized Parameters:\n")
    for i, key in enumerate(opt_order):
        logfile.write(f"    {key}: {res_gp.x[i]}\n")
