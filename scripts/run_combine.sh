#!/usr/bin/env bash
set -euo pipefail

pushd ~/combine_area/ &>/dev/null
eval `scramv1 runtime -sh` &>/dev/null
popd &>/dev/null


combine -M AsymptoticLimits $1
combine -M Significance $1
