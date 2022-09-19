#!/usr/bin/env python3
import argparse
import subprocess
import analysis_suite.commons.user as user
from pathlib import Path

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
parser.add_argument('-r', '--rerun', action="store_false")
args = parser.parse_args()

for typ in args.types:
    for year in args.years:
        output_dir = user.hdfs_area / f"{args.analysis}_{year}_{args.filename}_{typ}"
        if not output_dir.exists():
            continue
        files = f"{output_dir}/*root "
        if args.rerun and Path(f"{output_dir}_rerun").exists():
            files += f"{output_dir}_rerun/*root"
        subprocess.call(f"hadd -f -v 1 {args.filename}_{typ}_{year}.root {files}", shell=True)
