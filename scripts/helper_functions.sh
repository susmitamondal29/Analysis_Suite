#!/bin/bash

function run_combine() {
    bash -c '
        pushd ~/combine_area/ &>/dev/null
        eval $(scramv1 runtime -sh 2>/dev/null)
        popd &>/dev/null
        eval $@' bash $@
}

# Check if the function exists (bash specific)
if declare -f "$1" > /dev/null
then
    # call arguments verbatim
    "$@"
else
    # Show a helpful error
    echo "'$1' is not a known function name" >&2
fi
