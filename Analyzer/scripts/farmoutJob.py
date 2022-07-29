#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path
import subprocess
from xml.dom.minidom import parse
from analysis_suite.commons.user import analysis_area, hdfs_area, submit_area, eos_area

analysis = "ThreeTop"
runfile_dir = analysis_area / "runfiles"
if not runfile_dir.exists():
    runfile_dir.mkdir()

runfile_options = set()
for f in runfile_dir.glob("*.dat"):
    name = f.stem
    runfile_options.add(name[:name.index("201")-1])

xml_filename = str((analysis_area/'Analyzer/src/classes_def.xml').resolve())
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

with open(analysis_area/'data'/'.analyze_info', 'w') as f:
    f.write(args.analysis)

for year in args.years:
    runfile = runfile_dir / f'{args.filename}_{year}.dat'
    if not runfile.exists():
        print(f"{runfile} not found!")
        continue
    runfile = runfile.resolve()

    analysis_dir = f"{analysis}_{year}_{args.filename}"

    shutil.rmtree(submit_area/f"{analysis_dir}-analyze", ignore_errors=True)
    shutil.rmtree(hdfs_area/analysis_dir, ignore_errors=True)

    farmout_call = f"farmoutAnalysisJobs {analysis_dir}"
    farmout_call += f' --input-file-list={runfile}'
    farmout_call += f' --infer-cmssw-path'
    farmout_call += f' --fwklite analyze.py'
    farmout_call += f' --input-basenames-not-unique'
    # farmout_call += f' --num-cpus=4'
    farmout_call += f' --output-dir={eos_area/analysis_dir}'


    subprocess.call(farmout_call, shell=True)
