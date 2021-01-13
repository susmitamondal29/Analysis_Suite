#!/usr/bin/env bash
set -euo pipefail

value=$1
analysis=$2
year=$3
group=$4
files=$5

ls
echo $@

export X509_USER_PROXY="userproxy"

i=0
for f in $(echo $files | tr "," "\n"); do
    echo $f
    newf=$(echo $f | sed 's@/hdfs@root://cmsxrootd.hep.wisc.edu/@')
    echo $newf
    xrdcp $newf tree_${i}.root
    i=$((i + 1))
done

echo
ls -l
echo


# ./run_suite.py analyze -a $analysis -d CONDOR -s CONDOR -y $year -f $group
