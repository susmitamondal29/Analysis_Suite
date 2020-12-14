#!/usr/bin/env python3
import os
import pickle
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE
import getpass
import htcondor
import numpy as np
from bin_packing import pack
from analysis_suite.commons import FileInfo

def get_mtime(path):
    if path.is_dir():
        return max([get_mtime(sub) for sub in path.iterdir()])
    elif path.exists():
        return int(path.stat().st_mtime)
    else:
        return 0

def run_cmd(filename, inpath_name=".", cmd=None, infilename=None):
    if infilename is None:
        infilename = filename
    outpath = Path("dist/{}".format(filename))
    inpath = Path("{}/{}".format(inpath_name, infilename))
    inpath = inpath if inpath.exists() else Path(inpath_name)

    if get_mtime(inpath) > get_mtime(outpath):
        if cmd is None:
            cmd = "cp {} {}".format(inpath, outpath)
        cmd = cmd.format(out = outpath)
        result = subprocess.run(cmd.split(), stdout=PIPE, stderr=PIPE)

run_cmd("inputs.py")
run_cmd("run_suite.py")
run_cmd("montecarlo_2016.py", inpath_name="data/FileInfo/montecarlo")
run_cmd("analysis_suite-0.1.0-py3-none-any.whl", inpath_name="analysis_suite",
        cmd = "poetry build -f wheel")
run_cmd("requirements.txt", infilename="pyproject.toml",
        cmd = "poetry export -f requirements.txt -o {out} -E analysis --without-hashes")


# Setup Proxy
proxy="{home}/private/userproxy".format(home=os.environ["HOME"])
voms_result = subprocess.run("voms-proxy-info --valid 1:00 --file {proxy}".format(proxy=proxy).split(),
                             stdout=PIPE, stderr=PIPE)
if voms_result.returncode != 0:
    password = getpass.getpass("Need voms password: ").encode()
    voms_init = "voms-proxy-init -voms cms --pwstdin --out {proxy} --valid 192:0".format(proxy=proxy)
    p = Popen([voms_init], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate(input=password)


binned_files = dict()
main_args = ["ThreeTop", "2018"]


# Setup Bins
info = FileInfo(analysis="ThreeTop", selection="all_2018")
file_w_size_dict = info.get_file_with_size()

file_sizes = sorted([size  for group in file_w_size_dict.values() for _, size in group])
number_files = 4
bin_size = np.median(file_sizes)*number_files
print(bin_size)
for key, file_list in file_w_size_dict.items():
    bins = pack(file_list, bin_size)
    binned_files[key] = [",".join(b.names) for b in bins]
    
with open('filename.pickle', 'wb') as handle:
    pickle.dump(binned_files, handle)

# Submit the jobs
schedd = htcondor.Schedd()
sub = htcondor.Submit()
sub["Executable"] = "condor_job.sh"
sub["GetEnv"] = "true"
sub["error"] = "test.err"
sub["output"] = "test.out"
sub["log"] = "test.log"
# sub["request_memory"] = "2GB"
# sub["request_disk"] = "5GB"
sub["transfer_input_files"] = "dist/"

sub["stream_error"] = "true"
sub["stream_output"] = "true"

with schedd.transaction() as txn:
    group = "zzz"
    for i, args in enumerate(binned_files[group]):
        sub['Arguments']= " ".join(main_args +[group, str(i), args])
        print(sub["Arguments"])
        sub["transfer_output_files"] = f"{group}_{i}.parquet"
    sub.queue(txn)
