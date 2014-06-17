#!/usr/bin/env python

"""
Created on 2014-06-08T15:32:27
"""

from __future__ import division, print_function
import sys
import argparse

try:
    from idlToPandas import *
except:
    print("You need to install idlToPandas")
    sys.exit(1)

try:
    import pymysql
except:
    print('You need pymysql installed')
    sys.exit(1)

try:
    import pandas as pd
except:
    print('You need pandas installed')
    sys.exit(1)

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


def chironVelocity(fileName, path=''):
    """PURPOSE: This is the main routine that drives everything.
    Restore a CHIRON IDL velocity structure save file, restore the
    instructions on how to map that velocity structure to the SQL
    database and add the contents to the database."""

    #The two SQL tables that the IDL velocity structure save files
    #are written to:
    vstTableNames = ['velocities', 'psfs']

    #The text files that store column names and variable
    #types in the SQL velocity and psf tables:
    vstTableFileNames = ['tables/VelocityTable.txt', 'tables/PsfTable.txt']

    #How tag names in the IDL save structure map
    #to column names in the SQL tables:
    mappingTableFileName = 'tables/table2db.txt'

    #restore map
    idlSqlMap = getIdlToSqlMapping(mappingTableFileName)

    #restore the SQL table information to fill before writing to the DB
    tableDict = getTables(vstTableNames, vstTableFileNames)

    #restore the IDL velocity structure save file
    pdf = idlToPandas(path+fileName)

    #get the observation_id elements from the SQL DB:
    obsids = getObservationIds(tableDict, pdf)

    #Loop through observations updating tableDict:
    for idx in range(len(pdf)):
        pass

    #Junk to get rid of pesky linter lines:
    obsids += 1
    idlSqlMap += 1


def getIdlToSqlMapping(mappingTableFileName):
    """This routine will retrieve the fields and
    variable types of the table of interest."""
    mapping = pd.read_csv(mappingTableFileName)
    return mapping


def getTables(tableNames, tableFileNames):
    """This routine reads in the tables and stores them as
       pandas dataFrames within a python dictionary."""
    tableDict = {}
    for idx in range(len(tableNames)):
        #print('Now adding table ' + self.tableNames[idx])
        newTable = pd.read_csv(tableFileNames[idx])
        #newTable.columns = ['fieldName', 'variableType', 'obsValue']
        newTable['obsValue'] = 'NULL'
        tableDict[tableNames[idx]] = newTable
    return tableDict


def getAeroDir():
    cmd = 'echo $AeroFSdir'
    #read in the AeroFSdir string and
    adir = subprocess.check_output(cmd, shell=True)
    #chop off the newline character at the end
    adir = adir[0:len(adir)-1]
    return adir


def connectChironDB():
    """connect to the database"""
    #retrieve credentials:
    adir = getAeroDir()
    credsf = open(adir+'.credentials/SQL/csaye', 'r')
    creds = credsf.read().split('\n')
    conn = pymysql.connect(host=creds[0],
                           port=int(creds[1]),
                           user=creds[2],
                           passwd=creds[3],
                           db=creds[4])
    #cur = conn.cursor()
    return conn


def getObservationIds(tableDict, pdf):
    """The purpose of this routine is to retrieve the observation_ids
    from the database for all observations in the VST structures. It
    will add the observation_ids as a new column in both the velocities
    and psfs tables."""

    #connect to the chiron database
    conn = connectChironDB()
    cur = conn.cursor()

    #now create a list of the OBNM names (e.g. 'achi140402.1234')
    obnmlist = []
    for row in range(pdf.shape[0]):
        rowobnm = pdf.OBNM[row]
        obnmlist.append(rowobnm)

    #now join all the obnms together in one giant string
    #for the WHERE query clause. Issuing one giant query
    #instead of one for each observation reduces run time
    #by as much as a factor of 10000:
    obnmstring = "' OR obnm = '".join(obnmlist)

    #create the command that will retrieve the proper observation
    #ids for adding the observations to the velocity and psf tables
    cmd = "SELECT observation_id FROM observations WHERE obnm = '" + str(obnmstring) + "'"

    #execute the command and fetch the observation_ids:
    cur.execute(cmd)
    obsIds = cur.fetchall()
    return obsIds


def createInsertCmd():
    """This routine will create the command needed to add
    the velocity structure information to the database."""
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
    return cmd


def addToDatabase(tableNames, tableDict):
    """After all information has been retrieved from the FITS files
    this method can be called to add the information to the database."""
    conn = connectChironDB()
    cur = conn.cursor()

    #first check to make sure the observation isn't already in the database:
    thisObnm = tableDict['velocities'].loc[np.where(tableDict['velocities'].fieldName == 'obnm')[0][0], 'obsValue']
    cmd = "SELECT observation_id FROM observations WHERE obsid = '"+str(thisObsId).strip()+"'"
    cur.execute(cmd)
    dbEntryLocation = cur.fetchall()
    if dbEntryLocation == ():
        for tidx in tableNames:
            print('-----------------------------------------')
            print("TABLE NAME: "+tidx)
            print('-----------------------------------------')

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='To restore a CHIRON velocity structure and add the' +
                    'contents to the database')
    parser.add_argument(
        'starname',
        help='The HD number or star you would like to restore.')
    parser.add_argument(
        'path',
        help='[Optional] The path to the file. If not specified' +
             ' it will use the current working directory.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python chironVelocity.py fileName path')
        sys.exit(2)

    args = parser.parse_args()

    chironVelocity(args.starname, args.path)
