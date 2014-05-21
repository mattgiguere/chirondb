#!/usr/bin/env python

"""
Created on 2014-05-14T15:44:41
"""

from __future__ import division, print_function
import pymysql
import subprocess
import sys
import argparse
import pandas

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


#try:
#    import numpy as np
#except ImportError:
#    print('You need numpy installed')
#    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    got_mpl = True
except ImportError:
    print('You need matplotlib installed to get a plot')
    got_mpl = False

params = {'backend': 'png',
          'axes.linewidth': 1.5,
          'axes.labelsize': 24,
          'axes.font': 'sans-serif',
          #'axes.fontweight' : 'bold',
          'text.fontsize': 22,
          'legend.fontsize': 14,
          'xtick.labelsize': 16,
          'ytick.labelsize': 16,
          'text.usetex': False,
          'font.family': 'Palatino'
          }
plt.rcParams.update(params)


def getTables():
    """PURPOSE: To create the CHIRON MySQL database."""

    #The new tables in the database:
    table_names = ['observations',
                   'ccdsections',
                   'environment',
                   'weather',
                   'seeing',
                   'exposuremeter',
                   'reduction']

    table_dict = {}

    #observations table:
    observationsTable = pandas.read_csv('tables/ObservationsTable.txt')
    table_dict[table_names[0]] = observationsTable

    #CCD Sections Table
    ccdSectionsTable = pandas.read_csv('tables/CCDSectionsTable.txt')
    table_dict[table_names[1]] = ccdSectionsTable

    #Environment Table
    environmentTable = pandas.read_csv('tables/EnvironmentTable.txt')
    table_dict[table_names[2]] = environmentTable

    #Weather Table
    weatherTable = pandas.read_csv('tables/WeatherTable.txt')
    table_dict[table_names[3]] = weatherTable

    #Seeing Table
    seeingTable = pandas.read_csv('tables/SeeingTable.txt')
    table_dict[table_names[4]] = seeingTable

    #Exposure Meter Table
    exposureMeterTable = pandas.read_csv('tables/ExposureMeterTable.txt')
    table_dict[table_names[5]] = exposureMeterTable

    #Reduction Table
    reductionTable = pandas.read_csv('tables/ReductionTable.txt')
    table_dict[table_names[6]] = reductionTable

    return table_names, table_dict


def createTable(table_name, table_dict, cur):
    currentTable = table_dict[table_name]
    currentKeys = currentTable['fieldName']
    currentVarTypes = currentTable['variableType']

    cur.execute("SHOW TABLES")
    preExistingTables = cur.fetchall()
    if (not((table_name,) in preExistingTables)):
        cur.execute("CREATE TABLE " + table_name +
                    " (" + currentKeys[0] + " " +
                    currentVarTypes[0]+")")

    cur.execute("DESCRIBE "+table_name)
    preexistingKeys = [x[0] for x in cur.fetchall()]
    for idx in range(len(currentKeys)):
        key = currentKeys[idx].strip()
        varType = currentVarTypes[idx].strip()
        print('***************************************')
        print(key)
        if key in preexistingKeys:
            print('***WARNING! KEY ALREADY EXISTED!***')
        else:
            print('Now adding '+key)
            cur.execute("ALTER TABLE " + table_name + " ADD (" +
                        key + ' ' + varType + ')')


def connectChironDB():
    ###connect to the database###
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
    cur = conn.cursor()
    return cur


def removeTableFields(table_name, table_dict, cur):
    currentTable = table_dict[table_name]
    currentKeys = currentTable['fieldName']

    cur.execute("SHOW TABLES")
    preExistingTables = cur.fetchall()
    if (not((table_name,) in preExistingTables)):
        cur.execute("CREATE TABLE " + table_name +
                    " (" + currentKeys[0] + " " +
                    currentTable[currentKeys[0]]+")")

    cur.execute("DESCRIBE "+table_name)
    preexistingKeys = [x[0] for x in cur.fetchall()]
    for idx in range(len(currentKeys)):
        key = currentKeys[idx].strip()
        print('***************************************')
        print(key)
        if key in preexistingKeys:
            print('Now removing '+key)
            cur.execute("ALTER TABLE " + table_name + " DROP " + key)
        else:
            print('***WARNING! KEY DID NOT EXIST!***')


def createDB():
    """This routine creates all tables in the chironDB that do not
    also exist on exoplanets."""
    table_names, table_dict = getTables()
    cur = connectChironDB()
    for tName in table_names:
        print('===============================')
        print('Now making ' + tName + ' table.')
        print('===============================')
        createTable(tName, table_dict, cur)


def dropTables():
    """A routine that will make quick work of dropping all tables
    if you would like to start from scratch!"""
    table_names, table_dict = getTables()
    cur = connectChironDB()
    cur.execute("SHOW TABLES")
    preExistingTables = cur.fetchall()
    for tName in table_names:
        if ((tName,) in preExistingTables):
            cur.execute("DROP TABLE " + tName)
        else:
            print("***TABLE " + tName + " did not exist!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates the CHIRON MySQL Database.')
    parser.add_argument(
        'tablenum',
        help='The table number to add. If not specified, ' +
        'create_chidb will attempt to add all tables.',
        nargs='?')
    parser.add_argument(
        'columnnum',
        help='The column number to add. If not specified, ' +
        'create_chidb will attempt to add all columns. ' +
        '(NOTE: This functionality does not currently work.',
        nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python filename.py tablenum columnnum')
        sys.exit(2)

    args = parser.parse_args()
    #arg1 = int(sys.argv[1])
    #arg2 = int(sys.argv[2])

    if len(sys.argv) < 2:
        createDB()
    else:
        table_names, table_dict = getTables()
        cur = connectChironDB()
        createTable(table_names[int(args.tablenum)], table_dict, cur)
