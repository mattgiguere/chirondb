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
import subprocess
import pymysql
import pandas as pd
import datetime
import os
import warnings
from numba import jit, void, int_, double, autojit
import time


__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


class storeSpectra:
        """PURPOSE: To read in spectra and write them to the DB."""
        def __init__(self):
            self.minDate = ''
            self.maxDate = ''
            self.reducedRoot = '/tous/mir7/fitspec/'
            self.rawRoot = '/raw/mir7/'
            self.reducedFileName = ''
            #create an empty dataframe for the spectra:
            self.specdf = pd.DataFrame()

        def getRedDirs(self):
            """PURPOSE: To get a list of all raw directories."""
            cmd = "ls -1d "+self.reducedRoot+"1[1-4]*"
            dirs = subprocess.check_output(cmd, shell=True)
            self.redDirs = dirs.split('\n')

        def getRedFiles(self):
            """PURPOSE: Return all files within the input directory."""
            cmd = "ls -1 "+cdir+'/'
            rawfiles = subprocess.check_output(cmd, shell=True)
            rawfiles = rawfiles.split('\n')[:-1]
            return rawfiles

        def getRawFileName(self):
            """PURPOSE: Calculate the rawfilename based
            on the reduced filename.
            redFileName: the input reduced filename."""
            #This happens to be the case for CHIRON:
            redFileName = self.reducedFileName
            date = redFileName[4:10]
            return self.rawRoot+date+'/'+redFileName[1:]

        def readSpectrum(self):
            """PURPOSE: To read in the spectrum."""
            date = self.reducedFileName[4:10]
            fullFilename = self.reducedRoot + date + '/' + self.reducedFileName
            hdulist = fits.open(fullFilename)
            scidata = hdulist[0].data
            return scidata

        @staticmethod
        def normSpec(wav, spec):
            """PURPOSE: To return a normalized spectrum."""
            #Turn off rank warnings from numpy polyfit:
            warnings.simplefilter('ignore', np.RankWarning)

            maxrms = 0.005
            z = blazeFit(wav, spec, maxrms, numcalls=150)
            #get wavelength range:
            wavspread = max(wav) - min(wav)

            #center wavelength range about zero:
            wavcent = wav - min(wav) - wavspread/2.

            #normalize the spectrum:
            normspec = spec/max(spec)

            #make a function based on those
            #polynomial coefficients:
            cfit = np.poly1d(z)
            return normspec/cfit(wavcent)

        @staticmethod
        def connectChironDB():
            """connect to the database"""
            #retrieve credentials:
            cmd = 'echo $AeroFSdir'
            #read in the AeroFSdir string and
            #chop off the newline character at the end
            cdir = subprocess.check_output(cmd, shell=True)
            cdir = cdir[0:len(cdir)-1]
            credsf = open(cdir+'.credentials/SQL/csaye', 'r')
            creds = credsf.read().split('\n')
            conn = pymysql.connect(host=creds[0],
                                   port=int(creds[1]),
                                   user=creds[2],
                                   passwd=creds[3],
                                   db=creds[4])
            #cur = conn.cursor()
            return conn

        def makeSpecDF(self):
            """PURPOSE: To put the reduced spectrum in a pandas DataFrame"""
            #filename = self.reducedFileName
            rawfilename = self.getRawFileName()
            scidata = self.readSpectrum()
            #create an empty dataframe to house the whole spec:
            onespecdf = pd.DataFrame()
            #Now cycle through the orders writing them to the DB
            for i in range(scidata.shape[0]):
                order = pd.DataFrame({'spec_id': None,
                                      'observation_id': None,
                                      'rawFilename': rawfilename,
                                      'echelleOrder': i,
                                      'wavelength': scidata[i, :, 0],
                                      'flux': scidata[i, :, 1],
                                      'normFlux': self.normSpec(scidata[i, :, 0],
                                                                scidata[i, :, 1]),
                                      'dateAdded': str(datetime.datetime.now())})
                onespecdf = onespecdf.append(order)
            #replace infinite values with 0:
            onespecdf = onespecdf.replace([np.inf, -np.inf], 0)
            self.specdf = onespecdf

            return onespecdf

        def reorderColumns(self):
            """PURPOSE: To reorder the columns to be in the same
                        order as the DB."""
            cols = ['spec_id', 'observation_id', 'rawFilename', 'echelleOrder',
                    'wavelength', 'flux', 'normFlux', 'dateAdded']

            self.specdf = self.specdf[cols]

        def writeSpectrum(self, chkExist=False):
            """PURPOSE: Writes a given file to the DB.
            Set chkExist to True if you want to check
            to make sure the file doesn't already exist
            in the DB before writing."""
            #establish DB connection:
            conn = self.connectChironDB()

            if chkExist is True:
                pass
            else:
                self.specdf.to_sql('spectra', conn, flavor='mysql',
                                   if_exists='append', index=False)

        def driveDay(self, date):
            """PURPOSE: To drive all the files from the input date."""
            cmd = "ls -1 "+self.rawRoot+date+'/'
            rawfiles = subprocess.check_output(cmd, shell=True)
            rawfiles = rawfiles.split('\n')[:-1]
            #print(rawfiles)
            for rfile in rawfiles:
                self.reducedFileName = 'a'+rfile
                fullFile = self.reducedRoot+self.reducedFileName[4:10]
                fullFile += '/a'+rfile
                print('Now on File: {}'.format(fullFile))
                if os.path.isfile(fullFile):
                    self.makeSpecDF()
                    self.writeSpectrum()
                    self.specdf = pd.DataFrame()
                else:
                    print('File {0} did not exist!'.format(fullFile))

        def driveDateRange(self):
            """PURPOSE: To drive a range of input dates."""
            #Get all the dates with data:
            cmd = "ls -1d /tous/mir7/fitspec/1[1-4]*"
            dirs = subprocess.check_output(cmd, shell=True)
            dirs = dirs.split('\n')
            #print('len of dirs: {0}'.format(len(dirs)))
            self.minDate = int(self.minDate)
            self.maxDate = int(self.maxDate)
            tic = time.clock()

            for cdir in dirs[:-1]:
                thisDate = cdir.split('/')[-1]
                if len(thisDate) == 6:
                    if int(thisDate) >= self.minDate and int(thisDate) <= self.maxDate:
                        self.driveDay(thisDate)

            toc = time.clock()
            print('It took {0} second to complete.'.format(toc - tic))


def driveSpectraStoring(minDate, maxDate):
    specObj = storeSpectra()
    specObj.minDate = minDate
    specObj.maxDate = maxDate
    specObj.driveDateRange()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'mindate',
        help='The starting date.')
    parser.add_argument(
        'maxdate',
        help='The end date.')
    if len(sys.argv) > 3:
        print('use the command')
        print('python storeSpectra.py mindate maxdate')
        sys.exit(2)

    args = parser.parse_args()

    driveSpectraStoring(int(args.mindate), int(args.maxdate))