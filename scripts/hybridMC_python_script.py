#!/astro/apps6/anaconda/bin/python2
from __future__ import print_function, division, absolute_import

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg") # IMPORTANT for server to be able plot
import matplotlib.pyplot as plt
plt.ioff() # turn interactive maptlotlib off
import seaborn
import sys

from UsefulFunctions import SFH # Calculates the CSF for plotting

bins = 22 # With the set binning this will get ~50 Myrs

def main():
    completeFile = sys.argv[1]
    plotCSFComplete(completeFile)


def plotCSFComplete(completeFile):
    """
    This method takes in a ".complete" file that is the final product of a fit analysis (this might be 
    a hybridMC run).  The cumulative stellar mass fraction will be calculated with an error analysis.
    Plotted is the CSF with the region of error and the ages about the 50th percentile are found, this includes
    the 50th percentile of the errors.  With 3 ages for "original", "plus", and "minus" the closest age is found which then gives us the
    initial mass.  A plot is then saved with the CSF and the SFH for the area of interest.
    """
    # Get the id from the path above.
    snr_id = completeFile.split("/")[-2]
    # Get the fit name for when saving.
    fitName = completeFile.split("/")[-1]
    # Get the file path
    path = "/".join(completeFile.split("/")[:-1]) + "/"

    # Generate the data for the SFH and CSF plots as well as grab the errors
    sfr = SFH(completeFile, zcmerge=True, bins=bins)
    sfr.calculateSFR()
    sfr_err_spots, sfr_err_sfr, sfr_plus, sfr_minus = sfr.getErrors()
    csf = SFH("textFiles/set001_fit_004_M151.complete", zcmerge=True, cumulative=True, bins=bins)
    csf.calculateCSF()
    time, plus, minus, time_errors = csf.getErrors()

    fig, ax = plt.subplots(1,2, figsize=(10,6))

    # Plot CSF with error region
    ax[0].fill_between(time, plus, minus, color='0.5', alpha=0.5)
    ax[0].plot(csf.getX(), csf.getY(), color='k')
    ax[0].axvline(time_errors[0], ymin=0, ymax=1, color='k', linestyle='--', linewidth=0.9)
    ax[0].axvspan(time_errors[2], time_errors[1], color='r', alpha=0.3)


    # Get the masses corresponding with the errors
    log_year = np.arange(6.6, 7.8, 0.05)
    log_year_string = [str(year).replace(".", "-") for year in log_year]

    # get the highest initial mass for each age assuming solar of 0.019
    masses = []
    isochrones = {}
    for year in log_year_string: 
        iso = pd.read_csv("../isochrones/z_0-19_%s" % year, delim_whitespace=True) # We should be running this from the script folder
        isochrones[year] = iso
        masses.append(iso['M_ini'].values[-1]) # add the highest mass
    linear_year = 10**log_year / 10**6

    masses = np.asarray(masses)
    plotMasses = np.interp(ax[0].get_xticks(), linear_year, masses)
    plotMasses = [round(mass, 1) for mass in plotMasses]

    # prepare ticks for top x axis
    ax2_ticks = np.linspace(ax[0].get_xticks()[0], ax[0].get_xticks()[-1], 2*ax[0].get_xticks().size - 1)
    ax2_mass = np.round(np.interp(ax2_ticks, linear_year, masses), 2)
    ax2 = ax[0].twiny()
    ax2.set_xticks(ax2_ticks[::2], minor=False)
    ax2.set_xticklabels(ax2_mass[::2], size=12)
    ax2.xaxis.grid(True, which='major')
    # add minor ticks
    ax2.set_xticks(ax2_ticks[1::2], minor=True)
    ax2.set_xticklabels(ax2_mass[1::2], size=10, minor=True)
    ax2.xaxis.grid(False)

    # hand draw minor grid axis
    minor_top_ticks = ax2.get_xticks(minor=True)
    for i, xtick in enumerate(minor_top_ticks):
        ax[0].axvline(xtick, linestyle='-.', color='w', zorder=(i+0.1)/100, linewidth=1.2)
        
    # adjust padding
    ax2.tick_params(which='major', pad=15)
    ax2.tick_params(which='minor', pad=0)
    ax2.set_xlabel(r"Mass ($M_\odot$)", fontsize=12)
    ax2.set_axisbelow(True)

    # get the actual values of mass to display on the graph
    # get the closest log year to the percentiles
    ### IMPORTANT: The time_errors are reversed here because later times give lower initial mass and vice-versa.
    closest = getClosestLogYearIndex((time_errors[2], time_errors[0], time_errors[1]), log_year)
    central_mass = (isochrones[log_year_string[closest[0]]]['M_ini'].values[-1], isochrones[log_year_string[closest[1]]]['M_ini'].values[-1],
                    isochrones[log_year_string[closest[2]]]['M_ini'].values[-1])

    # Print the mass values on the plot
    ax[0].text(35, 0.9, snr_id, fontsize=12, zorder=10)
    ax[0].text(30, 0.85, r"$M_\odot=%.1f^{+%.1f}_{-%.1f}$" % (central_mass[1], central_mass[0]-central_mass[1], central_mass[1]-central_mass[2]),
               fontsize=12, zorder=10)

    ax[0].set_ylim([0.0, 1.0])
    ax[0].set_xlim([0, max(ax2_ticks)]) # IMPORTANT: The x upper limit needs to be set to the max tick of ax2 or the two horizontal axes misalign.
    ax[0].set_ylabel(r"Cumulative Stellar Mass Fraction")
    ax[0].set_xlabel(r"Time (Myrs)")

    ax[1].plot(sfr.getX(), sfr.getY(), color='k')
    ax[1].errorbar(sfr_err_spots, sfr_err_sfr, yerr=[sfr_minus.tolist(), sfr_plus.tolist()], linestyle='none', fillstyle='none',
                   color='k', capsize=0, linewidth=0.8)
    ax[1].set_xlabel("Time (Myrs)")
    ax[1].set_ylabel(r'Star Formation Rate ($M_{\odot}\ / \ yr$)')

    plt.tight_layout()

    plt.savefig(path+fitName)

def getClosestLogYearIndex(percentiles, log_year):
    """
    Pass in percentiles as (84th, 50th, 16th) with a log_year that will be compared to.
    Percentiles are assumed to be in millions of years and will be converted to log_year.
    """
    percentiles = np.log10(np.asarray(percentiles) * 10**6) # convert to log years

    distances = (np.abs(log_year - percentiles[0]), np.abs(log_year - percentiles[1]), np.abs(log_year - percentiles[2]))

    idx = (np.argmin(distances[0]), np.argmin(distances[1]), np.argmin(distances[2]))
    return idx

if __name__ == "__main__":
    main()
