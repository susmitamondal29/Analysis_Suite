#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path
import subprocess
from analysis_suite.commons.setup_functions import get_analyses
import analysis_suite.commons.user as user

runfile_dir = user.analysis_area / "runfiles"
if not runfile_dir.exists():
    runfile_dir.mkdir()

# runfile_options = set()
# for f in runfile_dir.glob("*.dat"):
#     name = f.stem
#     runfile_options.add(name[:name.index("201")-1])

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True,
                    # choices = list(runfile_options),
                    help="output filename")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_argument('-t', '--types', default="mc,data",
                    type=lambda x : [i.strip() for i in x.split(',')],)
parser.add_argument('-r', '--rerun', action='store_true')
parser.add_argument('-a', '--analysis', required=True, choices=get_analyses())
args = parser.parse_args()

with open(user.analysis_area/'data'/'.analyze_info', 'w') as f:
    f.write(args.analysis)

farmout_requirements = '(MY.RequiresSharedFS=!=true || TARGET.HasAFS_OSG) && (TARGET.OSG_major=!=undefined || TARGET.HAS_OSG_WN_CLIENT=?=True || TARGET.IS_GLIDEIN=?=true) && (TARGET.HasParrotCVMFS=?=true || (TARGET.CMS_CVMFS_Exists && TARGET.CMS_CVMFS_Revision >= 112885 )) && (TARGET.OpSysMajorVer == 7)'

for typ in args.types:
    for year in args.years:
        analysis_dir = f"{args.analysis}_{year}_{args.filename}_{typ}"
        nfs_scratch = user.submit_area/f'{analysis_dir}-analyze'

        if args.rerun:
            runfile = runfile_dir / f'{args.filename}_{typ}_rerun_{year}.dat'
            jobs = {d.name for d in nfs_scratch.iterdir() if d.is_dir()}
            files = {f.stem for f in (user.hdfs_area/analysis_dir).iterdir()}
            unrun_files = jobs - files
            with open(runfile, 'w') as infile:
                for ana in unrun_files:
                    with open(nfs_scratch / ana / f'{ana}.inputs') as f:
                        infile.write(f.readline())
            analysis_dir += '_rerun'
        else:
            runfile = runfile_dir / f'{args.filename}_{typ}_{year}.dat'
            if not runfile.exists():
                print(f"{runfile} not found!")
                continue
        runfile = runfile.resolve()

        shutil.rmtree(user.submit_area/f"{analysis_dir}-analyze", ignore_errors=True)
        shutil.rmtree(user.hdfs_area/analysis_dir, ignore_errors=True)

        farmout_call = f"farmoutAnalysisJobs {analysis_dir}"
        farmout_call += f' --input-file-list={runfile}'
        farmout_call += f' --infer-cmssw-path'
        farmout_call += f' --fwklite analyze.py'
        farmout_call += f' --input-basenames-not-unique'
        farmout_call += f' --base-requirements="{farmout_requirements}"'
        # farmout_call += f' --use-singularity=CentOS7'
        farmout_call += f' --output-dir={user.eos_area/analysis_dir}'

        subprocess.call(farmout_call, shell=True)

        if args.rerun:
            runfile.unlink()
