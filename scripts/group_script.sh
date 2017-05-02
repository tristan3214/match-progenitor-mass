#!/usr/bin/env bash

### List of passed in variables
# $1 - Path name to working directory
# $2 - Base name of fit.
# $3 - Photometry file.
# $4 - Calcsfh parameter file.

# Get the scripts full path
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

echo "Passed in"
echo "${1}, ${2}, ${3}"

grouping=$1 # what kind of grouping is this (eg bestdAv)
directory=$2 # directory to likewise fit
commands=( "${@:3}" ) # grab all the commands
echo "command 1: ${commands[0]}"
echo "command 2: ${commands[1]}"

#echo "Passed in quantities ${1}, ${2}, ${3}, and ${4}"
#"$SCRIPTPATH/ProcessDAv.py" $1 $2 $3 $4
"$SCRIPTPATH/group_python_script.py" $grouping $directory ${commands[0]}
