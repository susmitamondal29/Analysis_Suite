#!/usr/bin/env bash
set -euo pipefail

user=dteague
base_path="/store/user/${user}"

if [ $# != 1 ]; then
    echo "Choose from the possible directories:"
    ls "/hdfs/$base_path"
    exit 0
fi
path=$base_path/$1
if [ ! -d "/hdfs/$path" ]; then
    echo "Path doesn't exist!"
    echo $path
    exit 0
fi

hdfs dfs -find $path -name "*root"
