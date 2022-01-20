#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path
import subprocess

analysis = "ThreeTop"
user = Path().home().owner()
runfile_dir = Path(__file__).parent / ".." / "runfiles"
if not runfile_dir.exists():
    runfile_dir.mkdir()

runfile_options = set()
for f in runfile_dir.glob("*.dat"):
    runfile_options.add(f.stem[:-5])

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True,
                    choices = list(runfile_options),
                    help="output filename")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
args = parser.parse_args()


for year in args.years:
    runfile = runfile_dir / f'{args.filename}_{year}.dat'
    if not runfile.exists():
        print(f"{runfile} not found!")
        continue
    runfile = runfile.resolve()

    analysis_dir = f"{analysis}_{year}_{args.filename}"
    output_dir = f'/store/user/{user}/{analysis_dir}'

    shutil.rmtree(Path(f"/nfs_scratch/{user}/{analysis_dir}-analyze"), ignore_errors=True)
    shutil.rmtree(Path(f"/hdfs/{output_dir}"), ignore_errors=True)

    farmout_call = f"farmoutAnalysisJobs {analysis_dir}"
    farmout_call += f' --input-file-list={runfile}'
    farmout_call += f' --infer-cmssw-path'
    farmout_call += f' --fwklite analyze.py'
    farmout_call += f' --input-basenames-not-unique'
    farmout_call += f' --output-dir={output_dir}'


    subprocess.call(farmout_call, shell=True)
