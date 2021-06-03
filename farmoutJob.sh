#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
    ls /hdfs/store/user/$USER
    exit 0
else
    anaDir=$1
    shift
fi


if [[ -d "/nfs_scratch/$USER/$anaDir-analyze" ]]; then
    rm -r "/nfs_scratch/$USER/$anaDir-analyze"
fi

farmoutAnalysisJobs $anaDir --infer-cmssw-path --fwklite analyze.py \
    --input-basenames-not-unique --extra-usercode-files="src/analysis_suite/data/scale_factors" $@
