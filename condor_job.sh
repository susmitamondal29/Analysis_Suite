#!/usr/bin/env bash
set -euo pipefail


echo $@
echo "YO"

# analysis=$1
# year=$2
# group=$3
# files=$4

# echo $@

# ls

# proxy_path="/afs/cern.ch/user/${USER:0:1}/$USER/private/userproxy"
# export X509_USER_PROXY=$proxy_path

# python3 -m venv env
# source env/bin/activate
# pip install analysis_suite*whl
# pip install -r requirements.txt

# for f in $(echo $files | tr ";" "\n"); do
#     echo "File is: $f"
# done

# echo "./run_suite.py analyze -a $analysis -d CONDOR -s CONDOR -y $year -f $group"
