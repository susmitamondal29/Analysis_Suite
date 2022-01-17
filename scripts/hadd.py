#!/usr/bin/env python3
import argparse
import subprocess

analysis = "ThreeTop"
user = Path().home().owner()
output_start = Path(f'/hadd/store/user/{user}')

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", required=True,
                    choices = list(runfile_options),
                    help="output filename")
parser.add_argument("-y", "--years", required=True,
                    type=lambda x : ["2016", "2017", "2018"] if x == "all" \
                               else [i.strip() for i in x.split(',')],
                    help="Year to use")
parser.add_arguement("-o", "--output", required=True,
                     help="Output file name (root not needed)")
args = parser.parse_args()

for year in args.years:
    output_dir = output_start / f"{analysis}_{year}_{args.filename}"
    if not output_dir.exist():
        continue
    subprocess.call("hadd -f {args.output}_{year}.root {output_dir}/*root", shell=True)
