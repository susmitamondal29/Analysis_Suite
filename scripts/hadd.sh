#!/usr/bin/env bash
set -euo pipefail

path_start=/hdfs/store/user/$USER
analysis="ThreeTop"
selection="NEWtopTagger-HT250-Bjet1-Leptons2"

for year in 2016 2017 2018; do
    analysis_dir="${analysis}_${year}_${selection}"
    if [ ! -d  $path_start/${analysis_dir}-analyze/ ]; then
        continue
    fi

    hadd -f result_${year}.root $path_start/${analysis_dir}-analyze/*
done

# hadd results
