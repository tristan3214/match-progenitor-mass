#!/astro/apps6/anaconda/bin/python2
from __future__ import print_function, division, absolute_import

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg") # IMPORTANT for server to be able plot
import matplotlib.pyplot as plt
plt.ioff() # turn interactive maptlotlib off
from scipy.interpolate import interp1d
from astropy.io import fits
import seaborn

