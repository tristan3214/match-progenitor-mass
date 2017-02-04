#!/usr/bin/env bash

### List of passed in variables
# $1 - Path name to working directory
# $2 - Base name of fit.

echo "Passed in quantities ${1} and ${2}"
./scripts/ProcessDAv.py $1 $2 $3
