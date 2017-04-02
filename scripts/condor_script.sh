#!/usr/bin/env bash
# Get the scripts full path
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

"$SCRIPTPATH/scripts/condor_python_script.py" $@
