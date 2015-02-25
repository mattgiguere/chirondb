#!/usr/bin/env python

"""
Created on 2014-06-08T15:32:27
"""

from __future__ import division, print_function
import sys
import argparse
import subprocess

try:
    from idlToPandas import idlToPandas as itp
except:
    print("You need to install idlToPandas")
    sys.exit(1)

try:
    from pyutil import connectChironDB as ccdb
except:
    print('You need matt\'s pyutils installed')
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

try:
    import numpy as np
except:
    print('You need numpy installed')
    sys.exit(1)

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = "Production"
__version__ = '0.1.1'


def chironVelocity(starName, path='', cdir=0, tag='', comment='', tagOnFilename=''):
    """PURPOSE: This is the main routine that drives everything.
    Restore a CHIRON IDL velocity structure save file, restore the
    instructions on how to map that velocity structure to the SQL
    database and add the contents to the database.

    starName: The HD number of the star (e.g. 10700 is Tau Ceti)

    path: The path to the vst file (e.g. '/tous/mir7/vel_post/')

    cdir: if set to 1, set path to ${AeroFSdir}data/CHIRPS/rvs/

    tag: the tag id for the Doppler analysis (e.g. 'a' is for the symmetric
          PSF FTS that has been used since early 2015)

    comment: an optional comment to include when writing to the DB

    tagOnFilename: optional string appended to end of filename
            (e.g., if tagOnFilename='agb', then the code will restore
            path+'/vst'+starName+'agb.dat')
    """

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
    if cdir == 1:
        adir = getAeroDir()
        path = adir+'data/CHIRPS/rvs/'
    fullFileName = path+'vst'+str(starName)+tagOnFilename+'.dat'
    print(fullFileName)
    pdf = itp.idlToPandas(fullFileName)

    #get the observation_id elements from the SQL DB:
    obsids = getObservationIds(tableDict, pdf)

    #Loop through observations updating tableDict:
    for oidx in range(len(pdf)):
        print("---------------------------------------------------")
        print("Now on observation "+str(oidx)+" of "+str(len(pdf)))
        print("---------------------------------------------------")
        #first insert the correct observation_id for
        #the current observation in the loop:
        tableDict['velocities'].loc[tableDict['velocities']['fieldName'] ==
            'observation_id', 'obsValue'] = obsids[oidx][0]
        tableDict['psfs'].loc[tableDict['psfs']['fieldName'] ==
            'observation_id', 'obsValue'] = obsids[oidx][0]

        #update the tag and comment:
        tableDict['velocities'].loc[tableDict['velocities']['fieldName'] ==
            'tag', 'obsValue'] = tag
        tableDict['psfs'].loc[tableDict['psfs']['fieldName'] ==
            'tag', 'obsValue'] = tag
        tableDict['velocities'].loc[tableDict['velocities']['fieldName'] ==
            'comment', 'obsValue'] = comment
        tableDict['psfs'].loc[tableDict['psfs']['fieldName'] ==
            'comment', 'obsValue'] = comment

        #now insert the rest of the values into tableDict
        for idx in range(len(idlSqlMap)):
            if idlSqlMap.fitsSourceFile[idx] == 'vst':
                #current SQL table name to write things to:
                cTbNm = idlSqlMap.sqlDestTable[idx]

                #location in the table to write the value to
                colName = idlSqlMap.sqlColumnName[idx]
                tabloc = np.where(tableDict[cTbNm].fieldName == colName)[0][0]

                #if the IDL structure contains an array
                #it will need to be broken up:
                if idlSqlMap.arrIndex[idx] > -1:
                    arrIdx = int(idlSqlMap.arrIndex[idx])
                    fullArr = list(pdf[idlSqlMap.fitsKeyName[idx]][oidx])
                    newObsVal = fullArr[arrIdx]
                else:
                    newObsVal = pdf[idlSqlMap.fitsKeyName[idx]][oidx]
                tableDict[cTbNm].loc[tabloc, 'obsValue'] = newObsVal

        print("File name: "+tableDict['velocities'].loc[tableDict['velocities']['fieldName'] ==
                'obnm', 'obsValue'])
        #connect to the chiron database
        conn = ccdb.connectChironDB(legacy=True)
        cur = conn.cursor()

        #check to see if the observation already exists in the velocities
        #and psfs tables. If so, we need to UPDATE the observation instead
        #of INSERTing a new one.
        obExists = sqlObsExists(obsids[oidx][0], 'velocities', tag=tag, comment=comment)

        #now INSERT/UPDATE the line in the velocities table:
        cmd = createInsertCmd(tableDict, 'velocities', update=obExists,
                              obsid=obsids[oidx][0])

        cur.execute(cmd)
        conn.commit()

        #now repeat for the psfs table:
        obExists = sqlObsExists(obsids[oidx][0], 'psfs', tag=tag, comment=comment)
        cmd = createInsertCmd(tableDict, 'psfs', update=obExists,
                              obsid=obsids[oidx][0])
        cur.execute(cmd)
        conn.commit()


def sqlObsExists(obsid, tableName, tag='', comment=''):
    """This routine will check to see if the observation already exists in
    the SQL tables. This is necessary in order to determine if we should
    UPDATE an existing line, or INSERT a new one."""

    cmd = "SELECT * FROM " + tableName
    cmd += " WHERE observation_id = " + str(obsid)
    cmd += " AND tag='" + str(tag) + "'"
    cmd += " AND comment='" + str(comment) +"';"

    #connect to the chiron database
    conn = ccdb.connectChironDB(legacy=True)
    cur = conn.cursor()

    cur.execute(cmd)
    obnms = cur.fetchall()
    return len(obnms) > 0


def createInsertCmd(tableDict, tableName, update=False, obsid=-1):
    """This routine will create the command needed to INSERT or UPDATE
    the velocities and psfs tables ."""
    tblnm = tableName

    if update is True:
        print("This observation already existed in the DB. Now updating it!")
        if obsid < 0:
            print("You need to enter the obsid.")
            return

        cmd = "UPDATE " + tblnm + " SET"
        for nidx in range(len(tableDict[tblnm]['obsValue'])):
            colName = tableDict[tblnm].loc[nidx, 'fieldName']
            newObsVal = str(tableDict[tblnm].loc[nidx, 'obsValue'])
            #add quotes to strings, otherwise MySQL will reject it:
            varType = tableDict[tblnm].loc[nidx, 'variableType'].strip()[0:3]
            if (varType == 'var'):
                newObsVal = "'"+newObsVal+"'"

            if colName != 'velocity_id' and colName != 'psf_id':
                cmd += " " + colName + "=" + newObsVal + ","

        #remove the last comma and space:
        cmd = cmd[:-1]

        #now tack on the search criteria:
        cmd += " WHERE observation_id="+str(obsid)
        #print(cmd)

    else:
        colNames = []
        obsVals = []
        cmd = "INSERT INTO "+tblnm+" ("
        for nidx in range(len(tableDict[tblnm]['obsValue'])):
            colNames.append(tableDict[tblnm].loc[nidx, 'fieldName'])
            newObsVal = str(tableDict[tblnm].loc[nidx, 'obsValue'])
            #add quotes to strings, otherwise MySQL will reject it:
            varType = tableDict[tblnm].loc[nidx, 'variableType'].strip()[0:3]
            if (varType == 'var'):
                newObsVal = "'"+newObsVal+"'"
            obsVals.append(newObsVal)

        #now finish up the command to INSERT the observation:
        cmd += ", ".join(colNames) + ") VALUES (" + ", ".join(obsVals)+")"

    print(cmd)
    return cmd


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


def getObservationIds(tableDict, pdf):
    """The purpose of this routine is to retrieve the observation_ids
    from the database for all observations in the VST structures. It
    will add the observation_ids as a new column in both the velocities
    and psfs tables."""

    #connect to the chiron database
    conn = ccdb.connectChironDB(legacy=True)
    cur = conn.cursor()

    #now create a list of the OBNM names (e.g. 'achi140402.1234')
    obnmlist = [rowobnm for rowobnm in pdf.OBNM]

    #now join all the obnms together in one giant string
    #for the WHERE query clause. Issuing one giant query
    #instead of one for each observation reduces run time
    #by as much as a factor of 10000:
    obnmstring = "' OR obnm = '".join(obnmlist)

    #create the command that will retrieve the proper observation
    #ids for adding the observations to the velocity and psf tables
    cmd = "SELECT observation_id FROM observations WHERE obnm = '"
    cmd += str(obnmstring) + "'"

    #execute the command and fetch the observation_ids:
    cur.execute(cmd)
    obsIds = cur.fetchall()

    if len(obsIds) != len(obnmlist):
        print("The resulting obsIds did not have the same length")
        print("As the input list of observations.")
        print("pdf length: "+str(len(pdf)))
        print("obnm list length: "+str(len(obnmlist)))
        print("obsids length: "+str(len(obsIds)))
        print("Now creating a temporary table to ")
        print("determine which observations are missing")
        temptabxsts = cur.execute("SHOW TABLES LIKE 'tempobnms'")
        if temptabxsts:
            print("tempobnms already exists. Now dropping before proceeding.")
            cur.execute("DROP TABLE tempobnms")
        else:
            print("tempobnms does not exist. Now creating it.")

        cur.execute("CREATE TABLE tempobnms (obnm varchar(64))")
        obList = "'),('".join(obnmlist)
        obList = "('" + obList + "')"
        cmd = "INSERT INTO tempobnms VALUES " + obList
        print(cmd)
        cur.execute(cmd)
        conn.commit()
        tempTblCmd = "SELECT t.obnm from tempobnms as t LEFT JOIN observations"
        tempTblCmd += " as o ON t.obnm=o.obnm WHERE o.obnm IS NULL"
        cur.execute(tempTblCmd)
        print("The observation that was in the input list")
        print("that is not in the observations table is:")
        print(cur.fetchall())
        conn.close()
        sys.exit(1)
    conn.close()
    return obsIds


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='To restore a CHIRON velocity structure and add the' +
                    ' contents to the chirondb MySQL database.')
    parser.add_argument(
        'starname',
        help='The HD number or star you would like to restore.')
    parser.add_argument(
        '--path',
        help='[Optional] The path to the file. If not specified' +
             ' it will use the current working directory.',
             nargs='?', const='')
    parser.add_argument(
        '--cdir',
        help='[Optional] If set to 1 this will set' +
             ' the path to the CHIRPS RV default path.',
             nargs='?', const=0, type=int)
    parser.add_argument(
        '--tag',
        help='[Optional] If set it will append a tag' +
             ' to the filename restored. It will also' +
             ' only overwrite entries in the database' +
             ' that share this same tag. The default' +
             ' values is empty (\'\')',
             nargs='?', const='', type=str)
    parser.add_argument(
        '--comment',
        help='[Optional] If set, adding a comment will' +
             ' append the given string to the comment' +
             ' column in the database. This will also' +
             ' only overwrite previous entries if they' +
             ' share the same comment.',
             nargs='?', const='', type=str)
    parser.add_argument(
        '--tof',
        help='[Optional] If set, adding a tof will' +
             ' append tof to the end of the filename.',
             nargs='?', const='', type=str)
    if len(sys.argv) > 11:
        print('use the command')
        print('python chironVelocity.py starhdnum --path --cdir --tag --comment --tof')
        sys.exit(2)

    args = parser.parse_args()

    if args.tof:
        tof = args.tof
    else:
        tof = ''
    ##Example: Type the following at the command line:
    ##python chironVelocity.py 10700 --path '/tous/mir7/vel_post/' 0 --tag 'a' --comment ''
    print('Star name: {}'.format(args.starname))
    print('path: {}'.format(args.path))
    print('tag: {}'.format(args.tag))

    chironVelocity(args.starname, path=args.path, cdir=args.cdir, tag=args.tag,
                   comment=args.comment, tagOnFilename=tof)
