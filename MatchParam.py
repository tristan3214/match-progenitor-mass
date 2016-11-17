#!/astro/users/tjhillis/anaconda2/bin/python2
from __future__ import print_function, division

import glob
import os
import sys

import numpy as np

"""
m-Mmin m-Mmax d(m-M) Avmin Avmax dAv
logZmin logZmax dlogZ
BF Bad0 Bad1
Ncmds
Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD)
Vmin Vmax V                              (per filter)
Imin Imax I                              (per filter)
Nexclude_gates exclude_gates Ncombine_gates combine_gates (per CMD)
Ntbins
To Tf (for each time bin)
"""

class MatchParam(object):
    """
    This class read from a master parameter file that can be interchanged via a symbolic link.
    The read in file is default.param and the user specifies their own master parameter file by.
    overwriting this symbolic link.  This ensures the user can easily swap out files with different
    defaults automatically.
    """
    def __init__(self, default, photFile, fakeFile):
        # Constructs a MATCH parameter file object from a default parameter file to reference the settings.
        # A fakeFile is also specified to construct the Vmin, Vmax, Imin, and Imax using completeness limits
        self.default = default # symbolic link or can be regularly specified parameter file
        self.phot = photFile # photometry file to be fed to calcsfh
        self.fake = fakeFile # fake file to be fed to calcsfh

        # dictionary that will fill with all the parameters (some are to be added in parseDefalut method)
        self.parameters = {"m-Mmin":None, "d(m-M)":None, "Avmin":None, "Avmax":None, "dAv":None,
                           "logZmin":None, "logZmax":None, "dlogZ":None, "BF":None, "Bad0":None, "Bad1":None,
                           "Ncmds":None, "background":None, "scale":-1}

        self.filterSet = []
        
        # flags to tell if there is something like zinc
        self.zinc = False
        self.ssp = False # if a an ssp flag is passed then this will be set to True

        self.savedTo = None
        self.name = None

        self._parseDefault()
        #print(self.parameters.keys())
        #print(self.parameters["dAv"])
        #print(self.parameters["background"])

    def change(self, string):
        """
        Pass a that has the parameter to change and the value to set delimited with an equals.
        Exampe: "dAv=0.1" (this would change the Av step to 0.1)
        """
        key = string.split("=")[0]
        value = string.split("=")[1]
        
        if key in self.parameters.keys():
            valType = type(self.parameters[key])
            self.parameters[key] = valType(value)
        else:
            print("Key not found check and try again")

    def get(self, key):
        """
        Pass in a key to retrieve the value of from the self.parameters dictionary."
        """
        if key in self.parameters.keys():
            return self.parameters[key]
        else:
            print("Did not find key:", key)
            #sys.exit(1)
    
            
            
    def save(self, path=None, name=None):
        """
        Used to save the current MatchParam object into a standard MATCH parameter file. Call after making any
        wanted changes to the generated MATCH parameter file.
        """
        if path is None:
            path = os.getcwd() + "/"
        if name is None:
            # defualts to parameter file named parameters_XX.param and creates symbolic link
            name = self._iterateParameter()
            
        self.savedTo = path + name
        self.name = name
        f = open(path + name, 'w')

        # line one (IMF m-Mmin m-Mmax d(m-M) Avmin Avmax dAv)
        f.write("%.2f %.2f %.2f %.3f %.3f %.2f\n" % (self.parameters["m-Mmin"], self.parameters["m-Mmax"], self.parameters["d(m-M)"],
                                                     self.parameters["Avmin"], self.parameters["Avmax"],self.parameters["dAv"]))

        # line two (logZmin logZmax dlogZ) w/zinc (logZmin logZmax dlogZ initMin initMax presMin presMax)
        if not self.zinc or self.ssp:
            f.write("%.2f %.2f %.2f\n" % (self.parameters["logZmin"], self.parameters["logZmax"], self.parameters["dlogZ"]))
        else:
            f.write("%.2f %.2f %.2f %.2f %.2f %.2f %.2f\n" % (self.parameters["logZmin"], self.parameters["logZmax"],
                                                self.parameters["dlogZ"], self.parameters["initMin"],
                                                self.parameters["initMax"], self.parameters["presMin"],
                                                self.parameters["presMax"]))
        # line three (BF Bad0 Bad1)
        f.write("%.2f %f %f\n" % (self.parameters["BF"], self.parameters["Bad0"], self.parameters["Bad1"]))

        # line four (Ncmds)
        f.write("%d\n" % (self.parameters["Ncmds"]))

        # line five to (five + Ncmds) (Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD))
        if self.parameters["Ncmds"] == 1:
            f.write("%.2f %.2f %d %.2f %.2f %s,%s\n" % (self.parameters["Vstep"], self.parameters["V-Istep"],
                                                self.parameters["fake_sm"], self.parameters["V-Imin"],
                                                self.parameters["V-Imax"], self.parameters["V"],
                                                self.parameters["I"]))
        else:
            for i in range(int(self.parameters["Ncmds"])):
                f.write("%.2f %.2f %d %.2f %.2f %s,%s\n" % (self.parameters["Vstep_" + str(i+1)], self.parameters["V-Istep_" + str(i+1)],
                                                    self.parameters["fake_sm_" + str(i+1)], self.parameters["V-Imin_" + str(i+1)],
                                                    self.parameters["V-Imax_" + str(i+1)], self.parameters["V_" + str(i+1)],
                                                    self.parameters["I_" + str(i+1)]))
        # lines for each filter (filterMin filterMax filter(per filter))
        for i, filter in enumerate(self.filterSet):
            f.write("%.1f %.1f %s\n" % (self.parameters[filter + "min"], self.parameters[filter + "max"],
                                    self.parameters[filter]))

        # exclude/combine gates (Nexclude exclude Ncombine combine (per CMD))
        for i in range(int(self.parameters["Ncmds"])):
            f.write("%d" % self.parameters["Nexclude"])
            if self.parameters["Nexclude"] != 0:
                exclude = self.parameters["exclude"]
                for j in range(len(exclude)//2):
                    f.write(" %.2f %.2f" % (exclude[2*j], exclude[2*j + 1]))
                    
            f.write(" %d" % self.parameters["Ncombine"])
            if self.parameters["Ncombine"] != 0:
                combine = self.parameters["combine"]
                for j in range(len(combine)//2):
                    f.write(" %.2f %.2f" % (combine[2*j], combine[2*j + 1]))
            f.write("\n")

        # number of time bins (Ntbins)
        f.write("%d\n" % self.parameters["Ntbins"])

        # time bins
        start = self.parameters["tstart"]
        end = self.parameters["tend"]
        for i, time in enumerate(start):
            f.write("  %.2f  %.2f\n" % (time, end[i]))

        # last line
        f.write("%s %s %s" % (self.parameters["lLine_1"], self.parameters["lLine_2"], str(self.parameters["scale"])))
        if self.parameters["background"] is not None:
            f.write("%s\n" % self.parameters["background"])
        else:
            f.write("\n")

        f.close()

    def _parseDefault(self):
        """
        Go through defualt parameter file and populate dictionary of parameters.
        """
        f = open(self.default, 'r')
        params = None
        
        # line one (IMF m-Mmin m-Mmax d(m-M) Avmin Avmax dAv)
        line = self._checkForEnd(f.readline())
        try:
            params = map(float, line.split())
            if len(params) < 6 or len(params) > 6:
                print("Missing/extra paramter(s) in line one of default parameter file:")
                print(line)
                sys.exit(1)
            else:

                self.parameters["m-Mmin"] = params[0]
                self.parameters["m-Mmax"] = params[1]
                self.parameters["d(m-M)"] = params[2]
                self.parameters["Avmin"] = params[3]
                self.parameters["Avmax"] = params[4]
                print("param 6", params[5])
                self.parameters["dAv"] = params[5]

        except ValueError:
            print("Could not convert one of the arguments to a float:")
            print(line)
            sys.exit(1)

        # line two (logZmin logZmax dlogZ) w/zinc (logZmin logZmax dlogZ initMin initMax presMin presMax)
        line = self._checkForEnd(f.readline())
        try:
            params = map(float, line.split())
            size = len(params)
            if size > 3: # zinc flag should be specified
                self.zinc = True
                if size > 7:
                    print("Extra parameter(s) in line two of default parameter file:")
                    print(line)
                    sys.exit(1)
                else: # add metallicity args plus zinc args
                    self.parameters["logZmin"] = params[0]
                    self.parameters["logZmax"] = params[1]
                    self.parameters["dlogZ"] = params[2]
                    self.parameters["initMin"] = params[3]
                    self.parameters["initMax"] = params[4]
                    self.parameters["presMin"] = params[5]
                    self.parameters["presMax"] = params[6]
            else:
                if size < 3:
                    print("Missing parameter(s) in line two of default parameter file:")
                    print(line)
                    sys.exit(1)
                else: # add metallicity args w/o zinc args
                    self.parameters["logZmin"] = params[0]
                    self.parameters["logZmax"] = params[1]
                    self.parameters["dlogZ"] = params[2]
        except ValueError:
            print("Could not convert a float in line one of the defualt parameter file:")
            print(line)
            sys.exit(1)

        # line 3 (BF Bad0 Bad1)
        line = self._checkForEnd(f.readline())
        try:
            params = map(float, line.split())
            size = len(params)
            if size > 3 or size < 3:
                print("Missing/extra paramter(s) in line three of default parameter file:")
                print(line)
                sys.exit(1)
            else:
                self.parameters["BF"] =  params[0]
                self.parameters["Bad0"] = params[1]
                self.parameters["Bad1"] = params[2]
        except ValueError:
            print("Could not convert a float in line one of the defualt parameter file:")
            print(line)
            sys.exit(1)

        # line 4 (Ncmds)
        line = self._checkForEnd(f.readline())
        try:
            params = map(float, line.split())
            size = len(params)
            if size > 1 or size < 1:
                print("Missing/extra paramter(s) in line three of default parameter file:")
                print(line)
                sys.exit(1)
            else:
                self.parameters["Ncmds"] = params[0]
        except ValueError:
            print("Could not convert an int in line four of the default paramter file:")
            print(line)
            sys.exit(1)

        # line 5 to Ncmds (Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD))
        numCMDs = int(self.parameters["Ncmds"])
        for i in range(numCMDs):
            line = self._checkForEnd(f.readline())
            try:
                params = map(str, line.split())
                size = len(params)
                if size > 6 or size < 6:
                    print("Missing/extra paramter(s) in line three of default parameter file:")
                    print(line)
                    sys.exit(1)
                else:
                    for j in range(size):
                        if j != 5:
                            params[j] = float(params[j])
                        else:
                            params[j] = str(params[j])
                    if numCMDs == 1: # keep normal naming scheme
                        self.parameters["Vstep"] = params[0]
                        self.parameters["V-Istep"] = params[1]
                        self.parameters["fake_sm"] = params[2]
                        self.parameters["V-Imin"] = params[3]
                        self.parameters["V-Imax"] = params[4]
                        filters = params[5].split(",")
                        self.parameters["V"] = filters[0]
                        self.parameters["I"] = filters[1]
                    else: # add numbers at the end e.g. V_1, V_2
                        self.parameters["Vstep_%d" % (i + 1)] = params[0]
                        self.parameters["V-Istep_%d" % (i + 1)] = params[1]
                        self.parameters["fake_sm_%d" % (i + 1)] = params[2]
                        self.parameters["V-Imin_%d" % (i + 1)] = params[3]
                        self.parameters["V-Imax_%d" % (i + 1)] = params[4]
                        filters = params[5].split(",")
                        self.parameters["V_%d" % (i + 1)] = filters[0]
                        self.parameters["I_%d" % (i + 1)] = filters[1]                
            except ValueError:
                print("Conversion of one of the arguments went wrong:")
                print(line)
                sys.exit(1)

        # line Ncmds to number of unique filters (Vmin Vmax V (per filter) # happens for every unique filter)
        filterSet = []
        seen = set()
        for i in range(numCMDs):
            if numCMDs == 1:
                filterV = self.parameters["V"]
                filterI = self.parameters["I"]
                if filterV not in seen:
                    filterSet.append(filterV)
                    seen.add(filterV)
                if filterI not in seen:
                    filterSet.append(filterI)
                    seen.add(filterI)
            else:
                filterV = self.parameters["V_%d" % (i + 1)]
                filterI = self.parameters["I_%d" % (i + 1)]
                if filterV not in seen:
                    filterSet.append(filterV)
                    seen.add(filterV)
                if filterI not in seen:
                    filterSet.append(filterI)
                    seen.add(filterI)

        self.filterSet = filterSet
        for i, filter in enumerate(filterSet):
            line = self._checkForEnd(f.readline())
            params = map(str, line.split())
            size = len(params)
            if size > 3 or size < 3:
                print("Missing/extra paramter(s) in line %d of default parameter file:" % (4 + numCMDs + i))
                print(line)
                sys.exit(1)
            try: # Vmin and Vmax are already specified (ie no generation of these from self.fake needed)
                for j in range(size):
                    if j < 2:
                        params[j] = float(params[j])
                    else:
                        params[j] = str(params[j])
                        
                    self.parameters[filter + "min"] = params[0]
                    self.parameters[filter + "max"] = params[1]
                    self.parameters[filter] = params[2]
            except ValueError: # if this is raised then need to generate Vmin, Vmax, etc.
                completeness = self._calculate50()
                maxes = self._calculateMaxes()
                self.parameters[filter + "min"] = maxes[i]
                self.parameters[filter + "max"] = completeness[i]
                self.parameters[filter] = filter

        # exclude/combine gates (Nexclude exclude Ncombine combine (per CMD))
        excludePoints = []
        combinePoints = []
        for i in range(numCMDs):
            line = self._checkForEnd(f.readline())
            try:
                count = 0
                params = map(float, line.split())

                self.parameters["Nexclude"] = int(params[0])
                count += 1

                if self.parameters["Nexclude"] != 0:
                    for j in range(4*self.parameters["Nexclude"]):
                        excludePoints.append(params[count])
                        excludePoints.append(params[count+1])
                        count += 2
                    self.parameters["exclude"] = excludePoints
                    print(self.parameters["exclude"])
                    
                if not params[count].is_integer():
                    print("Ncombine found to not be an integer this suggests user input error...")
                    print(line)
                    sys.exit(1)

                self.parameters["Ncombine"] = int(params[count])
                count += 1

                if self.parameters["Ncombine"] != 0:
                    for j in range(4*self.parameters["Ncombine"]):
                        combinePoints.append(params[count])
                        combinePoints.append(params[count+1])
                        count += 2
                    self.parameters["combine"] = combinePoints
            except ValueError:
                print("Could not convert float(s) in exclude/combine gates line of the defualt parameter file:")
                print(line)
                sys.exit(1)

                
                
        # number of time bins (Ntbins)
        line = self._checkForEnd(f.readline())
        try:
            params = map(int, line.split())
            size = len(params)
            if size > 1 or size < 1:
                print("Missing/extra paramter(s) in line %d of default parameter file:" % (4 + numCMDs + i))
                print(line)
                sys.exit(1)
            self.parameters["Ntbins"] = params[0]

        except ValueError:
            print("Could not convert int in time bin count line of the defualt parameter file:")
            print(line)
            sys.exit(1)

        # time bins
        start = [] # beginning of time bin
        end = [] # end of time bin
        for i in range(self.parameters["Ntbins"]):
            line = self._checkForEnd(f.readline())
            try:
                params = map(float, line.split())
                size = len(params)
                if size > 2 or size < 2:
                    print("Missing/extra paramter(s) in line %d of default parameter file:" % (4 + numCMDs + i))
                    print(line)
                    sys.exit(1)

                start.append(params[0])
                end.append(params[1])
            except ValueError:
                print("Could not convert a float for time bins:")
                print(line)
                sys.exit(1)
        self.parameters["tstart"] = start
        self.parameters["tend"] = end

        # last line
        line = self._checkForEnd(f.readline())
        try: # no background given
            params = map(str, line.split())
            size = len(params)
            if size > 3 or size < 3:
                print("Missing/extra paramter(s) in las line")
                print(line)
                sys.exit(1)
            self.parameters["lLine_1"] = params[0]
            self.parameters["lLine_2"] = params[1]
            idx = self._testTillString(params[2])
            
            if idx is not None: # if the returned idx is None then no string was found in the last line arg3
                try:
                    self.parameters["scale"] = float(params[2][:idx])
                    self.parameters["background"] = params[2][idx:]
                except ValueError: # this assumes somebody indicates "scale" in last line to determine the scale at a later time
                    self.parameters["scale"] = None
                    self.parameters["background"] = params[2][5:] # "scale" is 5 char long
            else:
                self.parameters["scale"] = float(params[2])

        except ValueError: # potential background
            print("Could not convert to string in last line:")
            print(line)
            sys.exit(1)

        f.close()

    def _testTillString(self, s):
        """
        Takes in a string s and will check when a string starts assuming there is a float before it.
        """
        size = len(s)
        idx = None
        for i in xrange(size):
            substring = s[:i+1]
            if i == 0 and substring == "-": # if there is a negative in front
                continue
            try:
                float(substring)
            except ValueError:
                idx = i
                break
        return idx
                
    def _checkForEnd(self, s):
        if s == "":
            print("Reached end of file unexpectedly in default parameter file...exiting")
            sys.exit(1)
        elif s == "\n":
            print("Unexpected blank line in default parameter file...exiting")
            sys.exit(1)
        else:
            print(s.strip())
            return s.strip()

    # hard coded too much; need to generalize to n unique filters
    def _calculateMaxes(self):
        """
        Calculates the brightest magnitude in the phot file, which is essentially the minium.
        """
        f336_cmd, f438_cmd, f814_cmd = np.loadtxt(self.phot, usecols=[0, 1, 2], unpack=True)

        f336_min = f336_cmd.min()
        f438_min = f438_cmd.min()
        f814_min = f814_cmd.min()

        return [f336_min, f438_min, f814_min]

    def _calculate50(self):
        """
        Calculates the 50 percent completeness limit for the passed in fake file.
        """

                # change this to get finer/coarser binning
        size_of_bin = 0.1 # set size of bin

        # read in fake file columns
        f336_in, f438_in, f814_in, f336_outin, f438_outin, f814_outin = np.loadtxt(self.fake,
                                                                                   usecols=[0, 1, 2, 3, 4, 5], unpack=True)

        ### Get the 50% completeness of F336W

        good_idx = np.where(f336_in < 30.0)[0]
        f336_in, f336_outin = f336_in[good_idx], f336_outin[good_idx]
        f336_brightest, f336_faintest = f336_in.min(), f336_in.max()
        number_of_bins = int(np.ceil((f336_faintest - f336_brightest) / size_of_bin))

        f336_mag = []
        f336_fraction = []

        begin_mag = f336_brightest
        end_mag = f336_brightest + size_of_bin
        for i in xrange(number_of_bins):
            idx = np.where((f336_in >= begin_mag) & (f336_in < end_mag))[0]
            recovered = f336_outin[idx]
            recovered = recovered[(recovered>=-1.0) & (recovered<=1.0)]
            if i == 0:
                f336_mag.append(begin_mag)
                f336_mag.append(end_mag)

                if idx.size <= 0:
                    f336_fraction.append(1.0)
                    f336_fraction.append(1.0)
                else:
                    f336_fraction.append(recovered.size / idx.size)
                    f336_fraction.append(recovered.size / idx.size)
            else:
                f336_mag.append(end_mag)

                if idx.size <= 0:
                    f336_fraction.append(1.0)
                else:
                    f336_fraction.append(recovered.size / idx.size)

            begin_mag = end_mag
            end_mag = end_mag + size_of_bin

        f336_mag, f336_fraction = np.asarray(f336_mag), np.asarray(f336_fraction)
        f336_50 = self._interpolate50Mag(f336_mag, f336_fraction)

        #### Get the 50% completeness for F438W

        good_idx = np.where(f438_in < 30.0)[0]
        f438_in, f438_outin = f438_in[good_idx], f438_outin[good_idx]
        f438_brightest, f438_faintest = f438_in.min(), f438_in.max()
        number_of_bins = int(np.ceil((f438_faintest - f438_brightest) / size_of_bin))

        f438_mag = []
        f438_fraction = []

        begin_mag = f438_brightest
        end_mag = f438_brightest + size_of_bin
        for i in xrange(number_of_bins):
            idx = np.where((f438_in >= begin_mag) & (f438_in < end_mag))[0]
            recovered = f438_outin[idx]
            recovered = recovered[(recovered>-1.0) & (recovered<1.0)]
            if i == 0:
                f438_mag.append(begin_mag)
                f438_mag.append(end_mag)

                if idx.size <= 0:
                    f438_fraction.append(1.0)
                    f438_fraction.append(1.0)
                else:
                    f438_fraction.append(recovered.size / idx.size)
                    f438_fraction.append(recovered.size / idx.size)
            else:
                f438_mag.append(end_mag)

                if idx.size <= 0:
                    f438_fraction.append(1.0)
                else:
                    f438_fraction.append(recovered.size / idx.size)

            begin_mag = end_mag
            end_mag = end_mag + size_of_bin

        f438_mag, f438_fraction = np.asarray(f438_mag), np.asarray(f438_fraction)
        f438_50 = self._interpolate50Mag(f438_mag, f438_fraction)

        ### Get the 50% completeness for F814W

        good_idx = np.where(f814_in < 30.0)[0]
        f814_in, f814_outin = f814_in[good_idx], f814_outin[good_idx]
        f814_brightest, f814_faintest = f814_in.min(), f814_in.max()
        number_of_bins = int(np.ceil((f814_faintest - f814_brightest) / size_of_bin))

        f814_mag = []
        f814_fraction = []

        begin_mag = f814_brightest
        end_mag = f814_brightest + size_of_bin
        for i in xrange(number_of_bins):
            idx = np.where((f814_in >= begin_mag) & (f814_in < end_mag))[0]
            recovered = f814_outin[idx]
            recovered = recovered[(recovered>-1.0) & (recovered<1.0)]
            if i == 0:
                f814_mag.append(begin_mag)
                f814_mag.append(end_mag)

                if idx.size <= 0:
                    f814_fraction.append(1.0)
                    f814_fraction.append(1.0)
                else:
                    f814_fraction.append(recovered.size / idx.size)
                    f814_fraction.append(recovered.size / idx.size)
            else:
                f814_mag.append(end_mag)

                if idx.size <= 0:
                    f814_fraction.append(1.0)
                else:
                    f814_fraction.append(recovered.size / idx.size)

            begin_mag = end_mag
            end_mag = end_mag + size_of_bin

        f814_mag, f814_fraction = np.asarray(f814_mag), np.asarray(f814_fraction)
        f814_50 = self._interpolate50Mag(f814_mag, f814_fraction)

        # Print interpolations
        #print("F336W 50%:", f336_50)
        #print("F438W 50%:", f438_50)
        #print("F814W 50%:", f814_50)

        return [f336_50, f438_50, f814_50]

    def _interpolate50Mag(self, mags, fracs):
        """
        Linearly extrapolates between the points that bound 0.5. 
        """
        idx1 = np.where(fracs < 0.5)[0][0]
        idx2 = np.where(fracs > 0.5)[0][-1]

        x1 = fracs[idx1]
        y1 = mags[idx1]

        x2 = fracs[idx2]
        y2 = mags[idx2]

        m = (y2 - y1) / (x2 - x1)
        b = (-m * x1 + y1)

        linear = lambda x: m * x + b
        return linear(0.5)

    def _iterateParameter(self):
        """
        Assumes format of base_XX.(param, fake, phot).
        """
        cd = os.getcwd() + '/'
        files = glob.glob(cd + "parameters_*.param")
        size = len(files)

        nextFile = ""
        if size > 0:
            numbers = [int(files[i].split("_")[1].split(".")[0]) for i in xrange(len(files))]
            #print(numbers)
            
            numbers = sorted(numbers, key=int)
            nextVal = numbers[-1] + 1

            end = ""
            if nextVal < 10:
                end = "_0%d" % nextVal
            else:
                end = "_%d" % nextVal

            nextFile = "parameters" + end + ".param"
        else:
            nextFile = "parameters_01.param"
        return nextFile
