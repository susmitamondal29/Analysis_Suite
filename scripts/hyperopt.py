#!/usr/bin/env python3

from datetime import datetime
import skopt
import math
from collections import OrderedDict
import numpy as np
import pprint

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import checkOrCreateDir
from analysis_suite.data.inputs import mva_params
from analysis_suite.BDT_utilities.DNN import KerasMaker


group_info = GroupInfo(analysis="ThreeTop")
groupDict = OrderedDict()
for groupName, samples in mva_params.groups:
    new_samples = list()
    for samp in samples:
        if samp in group_info.group2MemberMap:
            new_samples += group_info.group2MemberMap[samp]
        else:
            new_samples.append(samp)
    groupDict[groupName] = new_samples

# Determine static and hyper parameter
timestamp = datetime.now()

CONFIG = {
    "model_name": "hpo_model.h5",
    "n_calls": 50,
    "n_starts": 50,
}

nVars = len(mva_params.usevar)

hyperParams = OrderedDict({
    "hidden_layers": np.array([1, 2]),
    "initial_nodes": np.array([nVars, nVars*10]),
    "node_pattern": np.array(["static", "dynamic"]),
    "batch_power": np.array([8, 11]),
    "learning_rate": np.array([0.001, 0.005, 0.01, 0.05]),
    "regulator": np.array(["dropout", "none"]),
    "activation": np.array(["softplus", "elu"]),
    "epochs": np.array([10, 20]),
})



logfile_name = "test.log"


# Save used parameters to file
config_file = "config.json"
with open( config_file, "w" ) as f:
    f.write(pprint.pformat(hyperParams))
    print( "[OK ] Parameters saved to dataset folder." )

# Start the logfile
with open(logfile_name, "w" ) as logfile:
    logfile.write("| ")
    logfile.write(" | ".join(hyperParams.keys()))
    logfile.write(" | AUC |\n")

# Determine optimization space
opt_space = []
opt_order = []
i = 0
for key, vals in hyperParams.items():
    if vals.dtype.type is np.str_ or len(vals) != 2:
        opt_space.append(skopt.space.Categorical(vals, name=key))
    else:
        opt_space.append(skopt.space.Integer(*vals, name=key))
    opt_order.append(key)
    


# Objective function
@skopt.utils.use_named_args(opt_space)
def objective(**X):
    print(">> Configuration:")
    print("{}".format(X))

    mvaRunner = KerasMaker(mva_params.usevar, groupDict, params=X)
    
    workdir = "test_bdt"
    mvaRunner.setup_files(workdir)
    mvaRunner.train()

    print( ">> Obtained ROC-Integral value: {}".format(mvaRunner.auc_test))
    with open(logfile_name, "a" ) as logfile:
        logfile.write("| ")
        logfile.write(" | ".join([str(X[keys]) for keys in hyperParams.keys()]))
        logfile.write(" | {:.3f} |\n".format(mvaRunner.auc_train))
        
    opt_metric = math.log(1 - mvaRunner.auc_test)
    print( ">> Metric: {:.4f}".format( opt_metric ) )
    return opt_metric


# Perform the optimization
start_time = datetime.now()

res_gp = skopt.gp_minimize(
    func = objective,
    dimensions = opt_space,
    n_calls = CONFIG["n_calls"],
    n_random_starts = CONFIG["n_starts"],
    verbose = True
)

# exit()

# Report results
with open(logfile_name, "a") as logfile:
    logfile.write("TTT DNN Hyper Parameter Optimization Parameters \n")
    # f.write("Static and Parameter Space stored in: {}\n".format(config_file))
    logfile.write("Optimized Parameters:\n")
    for i, key in enumerate(opt_order):
        logfile.write("    {}: {}\n".format(key, res_gp.x[i]))

# with open(os.path.join(args.dataset, subDirName, "optimized_params_" + CONFIG["tag"] + ".json"), "w") as f:
#     f.write(write_json(dict([(key, res_gp.x[val]) for key, val in opt_order.iteritems()]), indent=2))
#     print( "[OK ] Finished optimization in: {}".format( datetime.now() - start_time ) )
