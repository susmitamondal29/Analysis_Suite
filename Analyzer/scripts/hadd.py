#!/usr/bin/env python3
import argparse
import subprocess
import analysis_suite.commons.user as user
from pathlib import Path
import shutil
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True,
                    help="output filename")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_argument('-a', '--analysis', required=True)
parser.add_argument('-t', '--types', default="mc,data",
                    type=lambda x : [i.strip() for i in x.split(',')],)
parser.add_argument('-d', '--workdir', default=datetime.now().strftime("%m%d"))
parser.add_argument('-r', '--rerun', action="store_false")
args = parser.parse_args()

base_dir = user.hdfs_workspace / args.filename
base_dir.mkdir(exist_ok=True)

for typ in args.types:
    for year in args.years:
        output_dir = base_dir / year / args.workdir
        output_dir.mkdir(parents=True, exist_ok=True)
        input_dir = user.hdfs_area / f"{args.analysis}_{year}_{args.filename}_{typ}"
        if not input_dir.exists():
            continue
        files = f"{input_dir}/*root "
        if args.rerun and Path(f"{input_dir}_rerun").exists():
            files += f"{input_dir}_rerun/*root"
        subprocess.call(f"hadd -f -v 1 {args.filename}_{typ}_{year}.root {files}", shell=True)
        shutil.move(f'{args.filename}_{typ}_{year}.root', output_dir)
