#!/usr/bin/env bash
set -euo pipefail

path_start=/hdfs/store/user/$USER
analysis="ThreeTop"
years='2016 2017 2018'

if [ "$#" -ne 1 ]; then
    echo "Need to specify an output directory name"
    exit 1
else
    echo "Files will be hadded from ${path_start}/${analysis}_YEAR_$1"
fi

outname=$1

for year in ${years}; do
    analysis_dir="${analysis}_${year}_${outname}"
    if [ ! -d  $path_start/${analysis_dir} ]; then
        continue
    fi

    hadd -f result_${year}.root $path_start/${analysis_dir}/*
done

# hadd results
