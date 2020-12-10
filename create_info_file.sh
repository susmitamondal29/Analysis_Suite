#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n'

base="/store/user/dteague/"
if [ "$#" -eq 0 ]; then
    hdfs dfs -ls -C $base
    exit
elif [ "$#" -ne 2 ]; then
    echo "Need output file to put stuff!"
    exit
else
    base="$base$1/"
    outfile=$2
fi


echo "info = {" > $outfile
for dir in $(hdfs dfs -ls -C $base); do
    samp=$(echo $dir | sed -rn 's@.*/([^/]+)_Tune.*$@\1@p')
    if [ -z "$samp" ]; then
        samp=$(echo $dir | sed -rn 's@.*/([^/]+)$@\1@p')
    fi
    echo "    '$samp': {" >> $outfile
    echo "        'file_path': [" >> $outfile
    for file in $(hdfs dfs -ls -R $dir); do
        filename="$(echo $file | awk '{print $8}')"
        size="$(echo $file | awk '{print $5}')"
        if [[ "$filename" == *".root" ]]; then
            echo "            ('$filename', $size)," >> $outfile
        fi
    done
    echo "        ]," >> $outfile
    echo "    }," >> $outfile
done
echo "}" >> $outfile
