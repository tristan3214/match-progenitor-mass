#!/usr/bin/env bash
# This is a script that is used to add some automatic processing to the ending of a fit.  This might look like creating a histogram of the SFH.
# The user has access to the file paths to both the input and output files for the fit using, for example, "$1".

#### List of available files in the form of their full path.
# $1 - calcsfh input parameter file
# $2 - calcsfh input photometry file
# $3 - calcsfh input fake star file
# $4 - calcsfh fit file name
# $5 - calcsfh console output file
# $6 - calcsfh zcombine output file
# $7 - calcsfh ".cmd" file
echo "Completed calcsfh fit"
echo $1
echo $2
echo $3
echo $4
echo $5
echo $6
echo $7
./scripts/hybridMC_python_script.py
