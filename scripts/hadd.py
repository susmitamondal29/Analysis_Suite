#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

analysis = "ThreeTop"
user = Path().home().owner()
output_start = Path(f'/hdfs/store/user/{user}')

runfile_options = set()
for dirname in output_start.glob(f"{analysis}_*"):
    dirname = dirname.name
    if "201" not in dirname:
        continue
    runfile_options.add(dirname[len(analysis)+6:])  # len(_yyyy_) = 6

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True,
                    choices = list(runfile_options),
                    help="output filename")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_argument("-o", "--output", required=True,
                     help="Output file name (root not needed)")
args = parser.parse_args()

for year in args.years:
    output_dir = output_start / f"{analysis}_{year}_{args.filename}"
    if not output_dir.exists():
        continue
    subprocess.call(f"hadd -f {args.output}_{year}.root {output_dir}/*root", shell=True)
