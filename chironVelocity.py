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

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


def chironVelocity(fileName, path=''):
    """PURPOSE: To restore a CHIRON velocity structure and add the
                contents to the database"""

    vstTableNames = ['velocities', 'psfs']
    vstTableFileNames = ['tables/VelocityTable.txt', 'tables/PsfTable.txt']
    tableDict = getTables(vstTableNames, vstTableFileNames)
    pdf = idlToPandas(path+fileName)
    for row in range(pdf.shape[0]):
        rowobnm = pdf.OBNM[row]

        #create the command that will retrieve the proper observation
        #id for adding the observation to the velocity and psf tables
        cmd = "SELECT observation_id FROM observations WHERE " +
            "obnm = '" + str(rowobnm) + "'"

        #now connect to the chiron database and get the observation id
        conn = connectChironDB()
        cur = conn.cursor()
        cur.execute(cmd)
        rowObsId = cur.fetchall()


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


def getSqlTable(tableName):
    """This routine will retrieve the fields and 
    variable types of the table of interest."""


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
    cmd = 'echo $AeroFSdir'
    credsf = open(cdir+'.credentials/SQL/csaye', 'r')
    creds = credsf.read().split('\n')
    conn = pymysql.connect(host=creds[0],
                           port=int(creds[1]),
                           user=creds[2],
                           passwd=creds[3],
                           db=creds[4])
    #cur = conn.cursor()
    return conn


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
