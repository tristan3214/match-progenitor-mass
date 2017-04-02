#!/usr/bin/env bash

### List of passed in variables
# $1 - Path name to working directory
# $2 - Base name of fit.
# $3 - Photometry file.
# $4 - Calcsfh parameter file.

# Get the scripts full path
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`


echo "Passed in quantities ${1}, ${2}, ${3}, and ${4}"
"$SCRIPTPATH/scripts/ProcessDAv.py" $1 $2 $3 $4
