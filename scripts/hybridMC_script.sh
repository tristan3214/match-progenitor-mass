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
# %8 - calcsfh ".dat" file when the -mcdata flag is used
echo "Completed calcsfh fit"
echo $1
echo $2
echo $3
echo $4
echo $5
echo $6
echo $7
echo $8

# Get the script path
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

# Assign the names of the files to be created
mcmcFile=$4.mcmc
moFile=$4.mo
mcmcZCFile=$4.mcmc.zc
completeFile=$4.complete

# Run hybridMC
hybridMC $8 $mcmcFile -nmc=1000 -dt=0.15 -tint=0.9 > $moFile

# Run zcombine on mcmcFile
zcombine -unweighted -medbest -jeffreys $mcmcFile > $mcmcZCFile

# Run zcmerge to complete the analysis main fit should come first
zcmerge $6 $mcmcZCFile -absolute > $completeFile

# Pass completeFile in to plot the data
"$SCRIPTPATH/hybridMC_python_script.py" $completeFile
