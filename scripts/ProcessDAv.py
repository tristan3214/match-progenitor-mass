#!/astro/apps6/anaconda/bin/python
from __future__ import print_function, division, absolute_import

import glob
import subprocess
import sys

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
plt.ioff() # turn interactive maptlotlib off
from scipy.interpolate import interp1d
from astropy.io import fits
import seaborn

from PlotSFR import SFH

__author__ = "Tristan J. Hillis"


"""
This funtion will take in a list that is sent to MatchRunner.py and find the best fit dAv and output it as a THE fit.
It will also plot the change in fit with dAv and Av as well as make cumulative star formation plots for all the plots.
"""
#dAvfile = open("textFiles/set001_fit_002_dAvs.ls", 'w')
#dAvfile.write("id dAv\n")
"""
def main():
    process_list = "/home/tristan/BenResearch/M83/mount/remnants/set001_fit_002_MatchRunner_list.txt"
    list = open("textFiles/set001_fit_002.ls", 'w')
    f = open(process_list, 'r')
    for line in f:
        line = line.split()
        fitName = line[3].split("/")[-1]
        path = line[3].split("/")[-2] + "/"
        path = "/home/tristan/BenResearch/M83/mount/remnants/" + path
        if "M160" in path:
            continue
        processDAv(path, fitName)
        list.write(path+fitName+"_fig2.png\n")
    f.close()
    list.close()
    dAvfile.close()
    #processDAv("/home/tristan/BenResearch/M83/mount/remnants/M151/", "set001_fit_001")
"""

def processDAv(path, baseName, photFile):
    """
    Takes in a path with a baseName that will follow standard dAv naming conventions.
    """
    dAvfile = open(path+baseName+"_dAvs.ls", 'a')
    metallicity = "z_0-19" # Defines the metallicity to use for plotting isochrones
    
    path = path.strip("")
    print("PATH:", path)
    files = glob.glob(path+baseName+"_dAv_?-??")
    
    files = np.asarray([file for file in files if "." not in file]) # get rid of extraneous files ending with a suffix
    #print(files)
    
    # order files in increasing dAv
    dAvs = np.asarray([float(file.split("/")[-1].split("_")[-1].replace("-", ".")) for file in files])
    #print(dAvs)

    # sort by increasing dAv
    idxs = np.argsort(dAvs)
    files = files[idxs]
    dAvs = dAvs[idxs]
    #print(files, dAvs)

    # get best fits values
    vec_getBestFit = np.vectorize(getBestFit) # vectorize function
    bestFits = vec_getBestFit(files)
    #print(bestFits)
    
    # make the fit with the best fit value the fit with the main string name.
    best_idx = np.argmin(bestFits)
    best_file = files[best_idx]
    best_files = glob.glob(best_file+"*")

    # print out the SNR with best dAv
    #print(repr(path),path.split("/"))
    name = path.split("/")[-2]
    best_dAv = dAvs[best_idx]
    dAvfile.write("%s %f\n" % (name, best_dAv))
    
    # change the names
    new_names = []
    for file in best_files:
        name = file.split("/")[-1].split("_")
        if "." in name[-1]:
            name[-1] = "." + name[-1].split(".")[-1]
            name.pop(-2)
            name = "_".join(name[:-1]) + name[-1]
        else:
            name.pop(-1)
            name.pop(-1)
            name = "_".join(name)
        new_names.append(path+name)
        
    #print()
    #print("BEST FILES:", best_files)
    #print()
    #print("NEW NAMES:", new_names)
    # copy best_files to new_names
    #os.chdir(path)
    for j, file in enumerate(best_files):
        name = new_names[j]
        #print(file, name)
        subprocess.call(['cp', file, name])
        
    #os.chdir("/home/tristan/BenResearch/M83/code/")
    

    plt.rc('font', family='sans-serif')
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)
    
    csfs = [SFH(file+".zc", cumulative=True, bins=24) for file in files]

    fig = plt.figure(figsize=(21.0, 9.0))
    #fig = plt.figure()
        
    # plot Cumulative stellar mass functions
    rainbow = iter(plt.cm.rainbow(np.linspace(0, 1, len(csfs))))
    ax = fig.add_subplot(131)
    for i, csf in enumerate(csfs):
        csf.calculateCSF()
        c = next(rainbow)
        ax.plot(csf.getX(), csf.getY(), color=c, linewidth=1.5, zorder=i/100 + 1)

    ax.set_axis_bgcolor('0.8')
    sm = plt.cm.ScalarMappable(cmap=plt.cm.rainbow, norm=plt.Normalize(vmin=dAvs[0], vmax=dAvs[-1]))
    sm.set_array(dAvs)
    cbar = fig.colorbar(sm)
    cbar.ax.tick_params(labelsize=14)

    plt.ylim([0.0, 1.0])
    plt.xlim([0, 70])
    plt.ylabel(r"Cumulative Stellar Mass", fontsize=20)
    plt.xlabel("Time (Myrs)", fontsize=20)
    ax.tick_params(labelsize=16)
    
    # get id for title
    split_path = path.split("/")
    split_path = [item for item in split_path if item != '']
    snr_id = split_path[-1]
    print("ID:", snr_id, split_path)
    #plt.suptitle(snr_id + ": " + baseName)

    #### Plot specific parts for the best dAv
    csf = csfs[best_idx]

    ### add to the top of the first panel the mass derived from the age using
    # get log years
    log_year = np.arange(6.6, 7.8, 0.05)
    log_year_string = [str(year).replace(".", "-") for year in log_year]
    #log_year = [str(year).replace(".", "-") for year in log_year]
    #print("HIGHER RES. LOG YEAR:", log_year)
    #log_year = np.log10(csf.getX() * 10**6)
    # get the highest initial mass for each age
    masses = []
    isochrones = {}
    for year in log_year_string: 
        iso = pd.read_csv("/astro/users/tjhillis/M83/isochrones/" + metallicity + "_%s" % year, delim_whitespace=True)
        isochrones[year] = iso
        masses.append(iso['M_ini'].values[-1]) # add the highest mass
    linear_year = 10**log_year / 10**6
    masses = np.asarray(masses)
    #print("SIZES:", masses.size, linear_year.size)
    plotMasses = np.interp(ax.get_xticks(), linear_year, masses)
    #plotMasses = np.interp(ax.get_xticks(), csf.getX(), masses)
    plotMasses = [round(mass,1) for mass in plotMasses]
    #print("INTERPOLATED MASS:", plotMasses)
    #print("LOG YEARS", log_year, log_year.size)
    #print("YEARS:", csf.getX())
    #print("MASSES:", masses, len(masses))
    
    
    #print(type(ax.get_xticks()))
    # prepare ticks for top x axis
    ax2_ticks = np.linspace(ax.get_xticks()[0], ax.get_xticks()[-1], 2*ax.get_xticks().size - 1)
    ax2_mass = np.round(np.interp(ax2_ticks, linear_year, masses), 2)
    ax2 = ax.twiny()
    ax2.set_xticks(ax2_ticks[::2], minor=False)
    ax2.set_xticklabels(ax2_mass[::2], size=16)
    ax2.xaxis.grid(False, which='major')
    # add minor ticks
    ax2.set_xticks(ax2_ticks[1::2], minor=True)
    ax2.set_xticklabels(ax2_mass[1::2], size=13, minor=True)
    ax2.xaxis.grid(False)
    #ax2.xaxis.grid(True, which='minor', linestyle='-', color='w') # There is a bug with zorder where it is ignored
    # hand draw minor grid axis
    minor_top_ticks = ax2.get_xticks(minor=True)
    for i, xtick in enumerate(minor_top_ticks):
        ax.axvline(xtick, linestyle='-.', color='w', zorder=(i+0.1)/100, linewidth=1.2)
    # adjust padding
    ax2.tick_params(which='major', pad=15)
    ax2.tick_params(which='minor', pad=0)
    ax2.set_xlabel(r"Mass ($M_\odot$)", fontsize=20)
    ax2.set_axisbelow(True)
    

    # Interpolate the percentiles
    central_mass = None
    if np.all(np.isnan(csf.getY())):
        central_mass = (0, 0, 0)
    else:
        percentiles = interpolate([0.84, 0.5, 0.16], csf.getX(), csf.getY())
        #print("Interpolate:", percentiles)

        ### plot percentiles with center as dotted line and grey band as area of error
        # plot vertical line for 50th percentile
        ax.axvline(x=percentiles[1], linestyle="--", color='0.0')

        # plot vertical translucent red region spanning the error
        ax.axvspan(xmin=percentiles[0], xmax=percentiles[2], color='r', alpha=0.2)

        # get the actual values of mass and display on the graph
        #central_mass = np.interp(percentiles, csf.getX(), masses)
        # get the closest log year to the percentiles
        closest = getClosestLogYearIndex(percentiles, log_year)
        central_mass = (isochrones[log_year_string[closest[0]]]['M_ini'].values[-1], isochrones[log_year_string[closest[1]]]['M_ini'].values[-1],
                       isochrones[log_year_string[closest[2]]]['M_ini'].values[-1])
        #print(closest, central_mass)

    ax.text(35, 0.9, snr_id, fontsize=20, zorder=10)
    ax.text(30, 0.85, r"$M=%.1f^{+%.1f}_{-%.1f}$" % (central_mass[1], central_mass[0]-central_mass[1], central_mass[1]-central_mass[2]),
            fontsize=20, zorder=10)
    #print(central_mass)

    #percentiles = np.interp(0.5, csf.getY(), csf.getX())
    #percentiles = np.percentile(csf.getX(), [84, 50, 16])
    #print("PERCENTILES:", percentiles)
    #print(np.all(np.diff(csf.getY() > 0)))

    #interp = interp1d(csf.getY(), csf.getX())
    #percentiles = np.array([0.84, 0.5, 0.16])
    #print(interp(percentiles))
    
    #plt.gca().tick_params(labelsize=20, which='major')
    
    # plot best fit values vs dAvs
    ax = fig.add_subplot(132)
    ax.scatter(dAvs, bestFits, color='k')
    ax.set_axis_bgcolor('0.8')
    plt.ylabel("Fit value (arbitrary)", fontsize=20)
    plt.xlabel("dAv", fontsize=20)
    plt.gca().tick_params(labelsize=16, which='major')

    # plot cmd with photometry file
    ax = fig.add_subplot(133)
    
    data = fits.getdata(path+"field.gst.fits")
    field_f438, field_f814 = data["F438W_VEGA"], data["F814W_VEGA"]
    phot_f438, phot_f814 = np.loadtxt(path+photFile, usecols=[1,2], unpack=True)

    field_mask = (field_f438 < 30.0) & (field_f814 < 30.0)
    phot_mask = (phot_f438 < 30.0) & (phot_f814 < 30.0)

    field_f438, field_f814 = field_f438[field_mask], field_f814[field_mask]
    phot_f438, phot_f814 = phot_f438[phot_mask], phot_f814[phot_mask]

    # plot field data as 2d histogram
    H, xedges, yedges = np.histogram2d(field_f438-field_f814, field_f814, bins=[75, 75])
    color = plt.cm.gray
    color.set_bad("w")
    col = ax.pcolormesh(xedges, yedges, np.ma.masked_values(H.T, 0), cmap=color)
    cbar = plt.colorbar(col)

    # plot SNR data as scatter plot
    ax.scatter(phot_f438-phot_f814, phot_f814, color='r', s=12)

    plt.xlabel("F438W - F814W", fontsize=18)
    plt.ylabel("F814W", fontsize=18)
    plt.xlim([-1.0, 6.0])
    plt.ylim([17.0, 26.0])

    ax.invert_yaxis()
    
    plt.gca().tick_params(labelsize=16, which='major')
    
    plt.tight_layout()

    plt.savefig(path+baseName+"_fig2", dpi=512)
    
    #plt.show()


def interpolate(interpVals, x, y):
    if type(interpVals) != list:
        idx1 = np.where(y >= interpVals)[0][-1] # get the upper value
        idx2 = np.where(y <= interpVals)[0][0] # get the lower value

        x1 = x[idx1]
        y1 = y[idx1]

        x2 = x[idx2]
        y2 = y[idx2]

        m = (y2 - y1) / (x2 - x1)
        b = (-m * x1 + y1)
        linear = lambda y: (y-b) / m
        return linear(interpVals)
    else:
        list_of_interps = []
        for interp in interpVals:
            idx1 = np.where(y >= interp)[0][-1] # get the upper value
            idx2 = np.where(y <= interp)[0][0] # get the lower value

            x1 = x[idx1]
            y1 = y[idx1]

            x2 = x[idx2]
            y2 = y[idx2]

            m = (y2 - y1) / (x2 - x1)
            b = (-m * x1 + y1)
            linear = lambda y: (y-b) / m
            list_of_interps.append(linear(interp))
        return list_of_interps

def getClosestLogYearIndex(percentiles, log_year):
    """
    Pass in percentiles as (84th, 50th, 16th) with a log_year that will be compared to.
    Percentiles are assumed to be in millions of years and will be converted to log_year.
    """
    percentiles = np.log10(np.asarray(percentiles) * 10**6) # convert to log years
    #print("CONVERTED PERCENTILES:", percentiles)

    distances = (np.abs(log_year - percentiles[0]), np.abs(log_year - percentiles[1]), np.abs(log_year - percentiles[2]))
    #print("DISTANCES:", distances)

    idx = (np.argmin(distances[0]), np.argmin(distances[1]), np.argmin(distances[2]))
    return idx
    
def getBestFit(fileName):
    f = open(fileName+".co", 'r')
    for line in f:
        if "Best" in line: # reached line where there is the best fit number
            fit = line.split()[-1]
            val = fit.split("=")[-1]
            return float(val)

path = sys.argv[1]
baseName = sys.argv[2]
photometry = sys.argv[3]
processDAv(path, baseName, photometry)

        
"""
if __name__ == "__main__":
    main()
"""
