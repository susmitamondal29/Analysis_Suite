#!/usr/bin/env bash
set -euo pipefail

analysis=$1
year=$2
group=$3
value=$4
files=$5

proxy_path="${HOME}/private/userproxy"
export X509_USER_PROXY=$proxy_path

python3 -m venv env
source env/bin/activate
pip install analysis_suite*whl &>/dev/null
pip install -r requirements.txt &>/dev/null

i=0
for f in $(echo $files | tr ";" "\n"); do
    echo $f
    ln -s $f tree_${i}.root
    i=$((i + 1))
done

ls -l

./run_suite.py analyze -a $analysis -d CONDOR -s CONDOR -y $year -f $group
mv "${group}.parquet" "${group}_${value}.parquet"

ls
