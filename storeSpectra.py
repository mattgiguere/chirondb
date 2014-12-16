#!/usr/bin/env python

"""
Created on 2014-12-16T12:10:33
"""

from __future__ import division, print_function
import sys
import argparse

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

from astropy.io import fits
from pyutil.blazeFit import blazeFit
from scipy.optimize import curve_fit
import subprocess
import pymysql
import pandas as pd
from pyutil.blazeFit import blazeFit
import datetime
import numpy as np
import os
import warnings
from numba import jit, void, int_, double, autojit
import time


__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


def storeSpectra(arg1, arg2):
    """PURPOSE: To """


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'arg1',
        help='This argument does something.')
    parser.add_argument(
        'arg2',
        help='This argument does something else. By specifying ' +
             'the "nargs=>" makes this argument not required.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python storeSpectra.py arg1 arg2')
        sys.exit(2)

    args = parser.parse_args()

    storeSpectra(int(args.arg1), args.arg2)
 