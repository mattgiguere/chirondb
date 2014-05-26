#!/usr/bin/env python

"""
Created on 2014-05-21T13:57:43
"""

from __future__ import division, print_function
import sys

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    got_mpl = True
except ImportError:
    print('You need matplotlib installed to get a plot')
    got_mpl = False

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'

params = {
    #'backend': 'png',
    'axes.linewidth': 1.5,
    'axes.labelsize': 24,
    'axes.font': 'sans-serif',
    'axes.fontweight': 'bold',
    'text.fontsize': 22,
    'legend.fontsize': 14,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'text.usetex': False,
    'font.family': 'Palatino'
}
plt.rcParams.update(params)


def chironObject(arg1, arg2):
    """PURPOSE: To """


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('')
        print('python chironObject.py arg1 arg2')
        print('')
        sys.exit(2)
    elif len(sys.argv) != 3:
        print('use the command')
        print('python filename.py arg1 arg2')
        sys.exit(2)

    arg1 = int(sys.argv[2])
    arg2 = str(sys.argv[1])

    chironObject(arg1, arg2)
