#!/usr/bin/env python

"""
Created on 2014-05-26T22:28:19
"""

from __future__ import division, print_function
import sys
import argparse
import os
import subprocess

try:
    from astropy.io.fits import getheader
except:
    print('You need astropy installed')
    sys.exit(1)

try:
    import pandas as pd
except:
    print('You need pandas installed')
    sys.exit(1)

try:
    import pymysql
except:
    print('You need pymysql installed')
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)


__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


class chironObject:
    """PURPOSE: An object containing all data pertaining to
    a CHIRON object and methods to retrieve that information
    from FITS files and save it to the CHIRON MySQL Database."""

    def __init__(self):
        self.rawFileName = ''
        self.reducedFileName = ''
        tableFrame = pd.read_csv('tables/tableList.txt')
        self.tableNames = tableFrame.tableName
        self.tableFileNames = tableFrame.tableFileName
        self.tableDict = {}
        self.reducedDir = '/tous/mir7/fitspec/'

    def setReducedFileName(self):
        """A method that does a little string manipulation to set
        the reduced filename based on the raw filename. Note:
        this still requires that the raw filename has been set
        by the user."""
        sarr = self.rawFileName.split('/')
        if os.path.exists(self.reducedDir+sarr[-2]+'/'+'r'+sarr[-1]):
            self.reducedFileName = self.reducedDir+sarr[-2]+'/'+'r'+sarr[-1]
        else:
            self.reducedFileName = self.reducedDir+sarr[-2]+'/'+'a'+sarr[-1]

    def getTables(self, resetTables=False):
        """This method reads in all the tables and stores them as
           pandas dataFrames within a python dictionary."""
        if self.tableDict != {} and resetTables is not True:
            print("You've already setup the tables.")
            print("set resetTables to True to reset.")
            return

        for idx in range(len(self.tableNames)):
            #print('Now adding table ' + self.tableNames[idx])
            newTable = pd.read_csv(self.tableFileNames[idx])
            #newTable.columns = ['fieldName', 'variableType', 'obsValue']
            newTable['obsValue'] = 'NULL'
            self.tableDict[self.tableNames[idx]] = newTable

    def getFitsToSql(self):
        """This method gets the conversion chart on how to map things from
        FITS files and other sources to SQL."""
        self.mapping = pd.read_csv('tables/table2db.txt')

    def getRawChironInformation(self):
        """This method updates the object with all information
           from the raw FITS file."""
        if self.rawFileName == '':
            print("You must first enter the raw filename.")
            return
        fitshead = getheader(self.rawFileName, 0, ignore_missing_end=True)
        self.getTables()
        self.getFitsToSql()
        #set the rawfilename for the observations table:
        self.tableDict['observations'].loc[self.tableDict['observations'].fieldName == 'rawfilename', 'obsValue'] = self.rawFileName
        self.tableDict['observations'].loc[self.tableDict['observations'].fieldName == 'obnm', 'obsValue'] = 'a' + self.rawFileName[17:31]
        for i in range(len(self.mapping)):
            if self.mapping.loc[i,'fitsSourceFile'] == 'raw':
                if self.mapping.loc[i,'fitsKeyName'].upper() in fitshead.keys():
                    currTab = self.tableDict[self.mapping.loc[i,'sqlDestTable']]
                    idx = currTab[currTab['fieldName'] == self.mapping.loc[i,'sqlColumnName']].index.tolist()
                    #comment fields have caused problems since there
                    #can be more than 1 and have special characters
                    if self.mapping.loc[i,'fitsKeyName'] == 'comment':
                        #first combine the multiple comments that might be in the FITS header:
                        comment = str(fitshead[self.mapping.loc[i,'fitsKeyName']])
                        #and make sure you remove commas. Otherwise it might crash when trying
                        #to add it to the database.
                        comment = comment.split(',')
                        comment = ' '.join(comment)
                        comment = comment.split('\n')
                        comment = ' '.join(comment)
                        comment = comment.split("'")
                        comment = ''.join(comment)
                        self.tableDict[self.mapping.loc[i,'sqlDestTable']].loc[idx, 'obsValue'] = comment
                    else:
                        #handles exceptions of missing FITS keys. Inserts NULL values in their place:
                        fitsval = str(fitshead[self.mapping.loc[i,'fitsKeyName']])
                        if fitsval.strip() == '':
                            fitsval = 'NULL'

                        #handles exceptions of error-ridden FITS headers having non-sensicle
                        #strings where FLOATs should be:
                        #print(idx[0])
                        #print(self.tableDict[self.mapping.loc[i,'sqlDestTable']].loc[idx[0], 'variableType'])
                        varType = self.tableDict[self.mapping.loc[i,'sqlDestTable']].loc[idx[0], 'variableType'].strip()[0:5]
                        if varType == 'FLOAT' and not valIsNumber(fitsval):
                            fitsval = 'NULL'
                        if varType == "varch" and fitsval.count("'"):
                            fitsval = fitsval.split("'")
                            fitsval = ''.join(fitsval)

                        self.tableDict[self.mapping.loc[i,'sqlDestTable']].loc[idx[0], 'obsValue'] = fitsval
        obs_ra = self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'obs_ra')[0][0], 'obsValue']
        print('obs_ra is: ', obs_ra)
        if (obs_ra != 'NULL' and obs_ra != 'ra'):
            obs_ra_decdeg = 15.*(float(obs_ra[0:2]) + float(obs_ra[3:5])/60 + float(obs_ra[6:])/3600)
            self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'obs_ra_decdeg')[0][0], 'obsValue'] = obs_ra_decdeg
        obs_dec = self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'obs_dec')[0][0], 'obsValue'].split(':')
        print('obs_dec is: ', obs_dec)
        if (obs_dec[0] != 'NULL' and obs_dec[0] != 'dec':
            if (float(obs_dec[0]) < 0):
                obs_dec_decdeg = float(obs_dec[0]) - float(obs_dec[1])/60. - float(obs_dec[2])/3600.
            else:
                obs_dec_decdeg = float(obs_dec[0]) + float(obs_dec[1])/60. + float(obs_dec[2])/3600.        
            self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'obs_dec_decdeg')[0][0], 'obsValue'] = obs_dec_decdeg
        ha = self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'ha')[0][0], 'obsValue'].split(':')
        print('ha is: ', ha)
        if (ha[0] != 'NULL' and ha[0] != 'hour_angle'):
            if (float(ha[0]) < 0):
                ha_decdeg = float(ha[0]) - float(ha[1])/60. - float(ha[2])/3600.
            else:
                ha_decdeg = float(ha[0]) + float(ha[1])/60. + float(ha[2])/3600.
            self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'ha_decdeg')[0][0], 'obsValue'] = ha_decdeg
        st = self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'st')[0][0], 'obsValue'].split(':')
        print('st is: ', st)
        if (st[0] !='NULL' and st[0] != 'sidereal_time'):
            st_dechr = float(st[0]) + float(st[1])/60. + float(st[2])/3600.
            self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'st_dechr')[0][0], 'obsValue'] = st_dechr

    def getReducedChironInformation(self):
        """This routine updates the object with all information
           from the raw FITS file."""
        if self.reducedFileName == '':
            print("You must first enter the reduced filename.")
            return
        if os.path.exists(self.reducedFileName):
            fitshead = getheader(self.reducedFileName, 0)
            self.tableDict['reduction'].loc[self.tableDict['reduction'].fieldName == 'reducedfilename', 'obsValue'] = self.reducedFileName
            for i in range(len(self.mapping)):
                if self.mapping.loc[i,'fitsSourceFile'] == 'reduced':
                    if self.mapping.loc[i,'fitsKeyName'].upper() in fitshead.keys():
                        currTab = self.tableDict[self.mapping.loc[i,'sqlDestTable']]
                        idx = currTab[currTab['fieldName'] == self.mapping.loc[i,'sqlColumnName']].index.tolist()
                        if self.mapping.loc[i,'fitsKeyName'] == 'comment':
                            self.tableDict[self.mapping.loc[i,'sqlDestTable']].loc[idx, 'obsValue'] = str(fitshead[self.mapping.loc[i,'fitsKeyName']])
                        else:
                            self.tableDict[self.mapping.loc[i,'sqlDestTable']].loc[idx, 'obsValue'] = fitshead[self.mapping.loc[i,'fitsKeyName']]
        else:
            print('Reduced file does not exist. Skipping...')

    def connectChironDB(self):
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

    def addToDatabase(self):
        """After all information has been retrieved from the FITS files
        this method can be called to add the information to the database."""
        conn = self.connectChironDB()
        cur = conn.cursor()

        #first check to make sure the observation isn't already in the database:
        thisObsId = self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'obsid')[0][0], 'obsValue']
        cmd = "SELECT observation_id FROM observations WHERE obsid = '"+str(thisObsId).strip()+"'"
        cur.execute(cmd)
        dbEntryLocation = cur.fetchall()
        if dbEntryLocation == ():
            for tidx in self.tableNames:
                print('-----------------------------------------')
                print("TABLE NAME: "+tidx)
                print('-----------------------------------------')

                #make a couple lists to add
                obsVals = []
                colNames = []
                cmd = "INSERT INTO "+tidx+" ("
                for nidx in range(len(self.tableDict[tidx]['obsValue'])):
                    colNames.append(self.tableDict[tidx].loc[nidx, 'fieldName'])
                    newObsVal = str(self.tableDict[tidx].loc[nidx, 'obsValue'])
                    #add quotes to strings, otherwise MySQL will reject it:
                    varType = self.tableDict[tidx].loc[nidx, 'variableType'].strip()[0:3]
                    if (varType == 'var'):
                        newObsVal = "'"+newObsVal+"'"
                    obsVals.append(newObsVal)

                #now finish up the command to INSERT the observation:
                cmd += ", ".join(colNames) + ") VALUES (" + ", ".join(obsVals)+")"
                print(cmd)

                #execute the command:
                cur.execute(cmd)

                #and commit the transaction to the database:
                conn.commit()

                #Now retrieve the AUTO_INCREMENTED observation_id and update tables
                #so they can be JOINed later:
                if tidx == 'observations':
                    obsid = self.tableDict['observations'].loc[np.where(self.tableDict['observations'].fieldName == 'obsid')[0][0], 'obsValue']
                    obscmd = "SELECT observation_id FROM observations WHERE obsid = '" +obsid+"'"
                    cur.execute(obscmd)
                    newObsId = cur.fetchall()[0][0]
                    print(newObsId)
                    for tidx in self.tableNames:
                        print("Table is: "+tidx)
                        self.tableDict[tidx].loc[np.where(self.tableDict[tidx].fieldName == 'observation_id')[0][0], 'obsValue'] = newObsId
        else:
            print(thisObsId+' is already in the database! Skipping...')


def valIsNumber(instring):
    try:
        float(instring)
        return True
    except:
        return False


def kapowObservation(rawName):
    myObs = chironObject()
    myObs.rawFileName = rawName
    myObs.getRawChironInformation()
    myObs.setReducedFileName()
    if os.path.exists(myObs.reducedFileName):
        myObs.getReducedChironInformation()
    myObs.addToDatabase()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='An object to gather all information about a CHIRON' +
        'observation and write it to the database.')
    parser.add_argument(
        'rawName',
        help='The name of the raw FITS file.')
    parser.add_argument(
        'kapow',
        help='(Optional) If set, this will auto-generate the reduced ' +
        'filename, retrieve all data, and everything to the database.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python chironObject.py rawName kapow')
        sys.exit(2)

    args = parser.parse_args()

    if len(sys.argv) > 2:
        print("KAPOW!!!")
        kapowObservation(args.rawName)
