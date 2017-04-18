#!/usr/bin/env bash
# Get the scripts full path
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

"$SCRIPTPATH/condor_python_script.py" $@
