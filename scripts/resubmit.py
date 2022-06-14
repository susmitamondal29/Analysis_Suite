#!/usr/bin/env python3

import argparse
import shutil
from pathlib import Path
import subprocess
from xml.dom.minidom import parse

analysis = "ThreeTop"
user = Path().home().owner()
base_dir = (Path(__file__).parent / "..").resolve()
runfile_dir = base_dir / "runfiles"
if not runfile_dir.exists():
    runfile_dir.mkdir()

runfile_options = set()
for f in runfile_dir.glob("*.dat"):
    runfile_options.add(f.stem[:-5])

xml_filename = str((base_dir/'Analyzer/src/classes_def.xml').resolve())
xml_classes = parse(xml_filename)
analysis_choices = [c.getAttribute("name") for c in xml_classes.getElementsByTagName('class')]

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True,
                    choices = list(runfile_options),
                    help="output filename")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_argument('-a', '--analysis', required=True, choices=analysis_choices)
args = parser.parse_args()

with open(base_dir/'data'/'.analyze_info', 'w') as f:
    f.write(args.analysis)


for year in args.years:
    analysis_dir = f"{analysis}_{year}_{args.filename}"
    output_dir = f'/store/user/{user}/{analysis_dir}'
    file_dir = Path('/hdfs') / f'store/user/{user}/{analysis_dir}'
    runfile = runfile_dir / f'{args.filename}_rerun_{year}.dat'
    nfs_scratch = Path('/nfs_scratch') / user / f'{analysis_dir}-analyze'

    jobs = {d.name for d in nfs_scratch.iterdir() if d.is_dir()}
    files = {f.stem for f in file_dir.iterdir()}
    unrun_files = jobs - files

    with open(runfile, 'w') as infile:
        for ana in unrun_files:
            with open(nfs_scratch / ana / f'{ana}.inputs') as f:
                infile.write(f.readline())

    # Setup rerunning directories
    analysis_dir += "_rerun"
    output_dir += "_rerun"

    shutil.rmtree(Path(f"/nfs_scratch/{user}/{analysis_dir}-analyze"), ignore_errors=True)
    shutil.rmtree(Path(f"/hdfs/{output_dir}"), ignore_errors=True)

    farmout_call = f"farmoutAnalysisJobs {analysis_dir}"
    farmout_call += f' --input-file-list={runfile}'
    farmout_call += f' --infer-cmssw-path'
    farmout_call += f' --fwklite analyze.py'
    farmout_call += f' --input-basenames-not-unique'
    farmout_call += f' --output-dir={output_dir}'

    # print(farmout_call)
    subprocess.call(farmout_call, shell=True)

    runfile.unlink()
    



