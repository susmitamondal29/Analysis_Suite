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
        cmd = "poetry build -f whl")
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


arguments = dict()
main_args = ["ThreeTop", "2016"]


# Setup Bins
info = FileInfo(analysis="ThreeTop", selection="full_2017")
file_sizes = sorted([size  for group in info.get_file_dict().values() for _, size in group])
number_files = 5
bin_size = np.median(file_sizes)*number_files
for key, file_list in info.get_file_dict().items():
    bins = pack(file_list, bin_size)
    arguments[key] = [",".join(b.names) for b in bins]


# Submit the jobs
# schedd = htcondor.Schedd()
# sub = htcondor.Submit()
# sub["Executable"] = "condor_job.sh"
# # sub["GetEnv"] = "true"
# sub["error"] = "test.err"
# sub["output"] = "test.out"
# sub["log"] = "test.log"
# # sub["request_memory"] = "2GB"
# # sub["request_disk"] = "5GB"
# # sub["transfer_input_files"] = "dist/"
# sub["stream_error"] = "true"
# sub["stream_output"] = "true"

# with schedd.transaction() as txn:
#     # for args in arguments["zzz"]:
#     #     sub['Arguments']= " ".join(main_args +["zzz", args])
#     sub.queue(txn)
# # condor_submit condor.sub



sleep_job = htcondor.Submit({
    "executable": "/usr/bin/sleep",
    "arguments": "1m",                # sleep for 1 minute
    "output": "sleep-$(ProcID).out",  # output and error separated by job, using the $(ProcID) macro
    "error": "sleep-$(ProcID).err",               # we send all of the HTCondor logs for every individual job to the same file still (not split up!)
    "log": "sleep.log",
    "request_cpus": "1",
    "request_memory": "128MB",
    "request_disk": "128MB",
})

print(sleep_job)


schedd = htcondor.Schedd()
with schedd.transaction() as txn:
    cluster_id = sleep_job.queue(txn, count=10)  # submit 10 jobs
print(cluster_id)

