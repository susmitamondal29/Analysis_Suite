#!/usr/bin/env bash
set -euo pipefail

analysis="ThreeTop"
selection="NEWtopTagger-HT250-Bjet1-Leptons2"
years='2016 2017 2018'

if [ "$#" -ne 1 ]; then
    echo "Need to specify an output directory name"
    exit 1
else
    echo "Files will be saved to /hdfs/store/user/$USER/${analysis}_YEAR_$1"
    echo "This function will delete the files in the above directories if the directory already exists"
    echo "    If you wish to keep these files, backing up is necessary"
    read -r -p "    Are you sure you wish to continue? [Y/n]" response
    if ! [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "y not read, exiting without running"
        exit 0
    fi
fi

outname=$1

for year in ${years}; do
    run_file="run_files_${year}.dat"
    analysis_dir="${analysis}_${year}_${selection}"

    if [ ! -f $run_file ]; then
        ./scripts/get_files_hdfs.sh $analysis_dir > $run_file
    fi

    rm -rf "/nfs_scratch/$USER/$analysis_dir-analyze"
    rm -rf "/hdfs/store/user/$USER/${analysis}_${year}_${outname}"

    farmoutAnalysisJobs "$analysis_dir" \
        --input-file-list=$run_file \
        --infer-cmssw-path --fwklite analyze.py \
        --input-basenames-not-unique \
        --output-dir="/store/user/$USER/${analysis}_${year}_$outname"
done
