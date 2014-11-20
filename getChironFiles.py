#!/usr/bin/env python

"""
Created on 2014-05-26T22:58:43
"""

from __future__ import division, print_function
import sys
import argparse
import subprocess

try:
    import chironObject as cdbo
except ImportError:
    print('You need to be in the same directory as chironObject.py')
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

try:
    from astropy.io.fits import getheader
except:
    print('You need astropy installed')
    sys.exit(1)

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


def getChironFiles(rootDir, minDate, maxDate):
    """PURPOSE: To cycle through all the CHIRON observations
    and add them to the database. An example of using this is
    to cd to the chirondb directory and at the command line
    type the following:

    python getChironFiles.py /raw/mir7/ 140730 140804

    where /raw/mir7/ is the root directory containing all the
    raw files, 140730 is the lower bound date and 140804 is the
    upper bound date.
    """

    if rootDir[-1] != '/':
        rootDir += '/'

    cmd = "ls -1d "+rootDir+"1[1-4]*"
    dirs = subprocess.check_output(cmd, shell=True)
    #print(dirs)
    dirs = dirs.split('\n')

    #now cycle through each directory listing the files:
    for cdir in dirs[:-1]:
        if len(cdir.split('/')[-1]) == 6:
            #print(int(cdir.split('/')[-1]) >= minDate)
            if int(cdir.split('/')[-1]) >= minDate and int(cdir.split('/')[-1]) <= maxDate:
                print((cdir.split('/')[-1]))
                cmd = "ls -1 "+cdir+'/chi*.fits'
                filesreturned = True
                try:
                    rawfiles = subprocess.check_output(cmd, shell=True)

                except subprocess.CalledProcessError:
                    print('Nothing useful in that directory. Skipping...')
                    filesreturned = False
                if filesreturned:
                    rawfiles = rawfiles.split('\n')[:-1]
                    #print(rawfiles)
                    for rfile in rawfiles:
                        print("cdbo.kapowObservation("+rfile+")")
                        cdbo.kapowObservation(rfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='To cycle through all CHIRON ' +
        'observations and add them to the database.')
    parser.add_argument(
        'rootDir',
        help='(Optional) Set this to the root directory to ' +
        'search for FITS files.', nargs='?')
    parser.add_argument(
        'minDate',
        help='(Optional) Set this to the minimum date you would ' +
             'like to add to the database.',
             nargs='?')
    parser.add_argument(
        'maxDate',
        help='(Optional) Set this to the maximum date you would ' +
             'like to add to the database.',
             nargs='?')
    if len(sys.argv) > 4:
        print('use the command')
        print('python getChironFiles.py rawDir minDate maxDate')
        sys.exit(2)

    args = parser.parse_args()

    getChironFiles(args.rootDir, int(args.minDate), int(args.maxDate))
