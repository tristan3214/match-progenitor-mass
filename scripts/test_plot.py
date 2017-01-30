#!/astro/apps6/anaconda/bin/python
from __future__ import print_function, division, absolute_import

import sys

from PlotSFR import SFH
from PlotSFR import plotAllCSF

zc = sys.argv[1]

csf = SFH(zc, cumulative=True, bins=1, label="Test")

plotAllCSF(SFH_list=[csf])

