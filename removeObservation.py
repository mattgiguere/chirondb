#!/usr/bin/env python

"""
Created on 2014-11-17T16:29:17
"""

from __future__ import division, print_function
import sys
import argparse
import subprocess

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
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


def removeObservation(obsid):
    """PURPOSE: To remove an observation from all tables."""

    #the MySQL command that will retrieve the observation_id
    #of the erroneous entry:
    cmd = "SELECT observation_id FROM observations "
    cmd += " WHERE obsid = " + str(obsid)

    #connect to the chiron database
    conn = connectChironDB()
    cur = conn.cursor()

    cur.execute(cmd)
    observation_id = cur.fetchall()

    #restore the list of table names from which
    #this observation_id will be removed
    tableFrame = pd.read_csv('tables/tableList.txt')
    self.tableNames = tableFrame.tableName


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='removeObservation.py will remove an observation' +
                    'from all tables in the database.')
    parser.add_argument(
        'obsid',
        help='The unique obsid of the observation.')
    if len(sys.argv) > 3:
        print('use the command')
        print('python removeObservation.py obsid')
        sys.exit(2)

    args = parser.parse_args()

    removeObservation(args.obsid)
