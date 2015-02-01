#!/usr/bin/env python

"""
Created on 2015-01-31T17:24:25
"""

from __future__ import division, print_function
import argparse
import sys
import numpy as np
import os

try:
    import pandas as pd
except ImportError:
    print('You need pandas installed')
    sys.exit(1)

try:
    import pyutil.connectChironDB as ccdb
except ImportError:
    print("You need Matt's pyutils installed.")
    sys.exit(1)

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'


def addEnviron(date):
    """PURPOSE:
    To add environmental information to the CHIRON DB. This routine
    reads in the insttemp, heater, chitemp, and dettemp logs and
    adds that information to the environ table of the chirondb
    MySQL DB. It can either be called from the command line:

    Example:
    %python addEnviron 150131

    Or imported and used in the python environment:

    Example:

    from addEnviron import addEnviron
    addEnviron(150131)

    If you are processing a bunch of dates, try using the `driveDates`
    routine:

    Example:

    %python driveDates 140101 150131 --logtodb environ

    or 

    from driveDates import driveDates
    driveDates(140101, 150131, logtodb='environ')

    """
    #filenames for the four environmental logs:
    instfn = '/tous/mir7/logs/temps/insttemp/insttemp'+date+'.log'
    htfn =  '/tous/mir7/logs/temps/heater/heater'+date+'.log'
    ctfn = '/tous/mir7/logs/temps/chitemp/chitemp'+date+'.log'
    dtfn = '/tous/mir7/logs/temps/dettemp/dettemp'+date+'.log'

    #restore the insttemp log:
    df_in = pd.read_table(instfn, sep='\s', engine='python', header=None)
    if (int(date) > 120519 & int(date) < 130416):
        df_in.columns = ['sampleTime', 'jnk1', 'gratingTemp', 'jnk2', 'tableCenterTemp', 'jnk3', 'enclosureTemp', 'jnk4',
                  'iodineCellTemp', 'jnk5', 'enclosureSetpoint', 'jnk6', 'iodineCellSetpoint', 'jnk7',
                  'enclosureTemp2', 'jnk8', 'tableTempLow', 'jnk9', 'structureTemp', 'jnk10', 'instrumentSetpoint',
                  'jnk11', 'instrumentTemp']
        df = df_in[['sampleTime', 'gratingTemp', 'tableCenterTemp', 'enclosureTemp',
                  'iodineCellTemp', 'enclosureSetpoint', 'iodineCellSetpoint',
                  'enclosureTemp2', 'tableTempLow', 'structureTemp', 'instrumentSetpoint',
                  'instrumentTemp']]
    else:
        df_in.columns = ['sampleTime', 'jnk1', 'gratingTemp', 'jnk2', 'tableCenterTemp', 'jnk3', 'enclosureTemp', 'jnk4',
                      'iodineCellTemp', 'jnk5', 'enclosureSetpoint', 'jnk6', 'iodineCellSetpoint', 'jnk7',
                      'enclosureTemp2', 'jnk8', 'tableTempLow', 'jnk9', 'structureTemp', 'jnk10', 'instrumentSetpoint',
                      'jnk11', 'instrumentTemp', 'jnk12', 'coudeTemp']
        df = df_in[['sampleTime', 'gratingTemp', 'tableCenterTemp', 'enclosureTemp',
                  'iodineCellTemp', 'enclosureSetpoint', 'iodineCellSetpoint',
                  'enclosureTemp2', 'tableTempLow', 'structureTemp', 'instrumentSetpoint',
                  'instrumentTemp', 'coudeTemp']]

    #restore and merge the heater log:
    if os.path.isfile(htfn):
        ht_in = pd.read_table(htfn, sep='\s', engine='python', header=None)
        ht_in.columns = ['sampleTime', 'jnk1', 'heaterSetpoint']
        ht = ht_in[['sampleTime', 'heaterSetpoint']]
        df = df.merge(ht, on='sampleTime', how='left')

    #restore and merge the chitemp log:
    if os.path.isfile(ctfn):
        ct_in = pd.read_table(ctfn, sep='\s', engine='python', header=None)
        ct_in.columns = ['sampleTime', 'jnk', 'barometer', 'jnk', 'echellePressure']
        ct = ct_in[['sampleTime', 'barometer', 'echellePressure']]
        df = df.merge(ct, on='sampleTime')

    #restore and merge the dettemp log:
    if os.path.isfile(dtfn):
        dt_in = pd.read_table(dtfn, sep='\s', engine='python', header=None)
        dt_in.columns = ['sampleTime', 'jnk1', 'ccdTemp', 'jnk2', 'neckTemp', 'jnk3', 'ccdSetpoint']
        dt = dt_in[['sampleTime', 'ccdTemp', 'neckTemp', 'ccdSetpoint']]
        df = df.merge(dt, on='sampleTime')

    #add an empty column for the timestamp of when the 
    #entry was added to the DB:
    df['dateAdded'] = None
    #connect to the CHIRON DB:
    engine = ccdb.connectChironDB()
    
    #see if any entries already exist:
    cmd = "SELECT sampleTime, environ_id FROM environ WHERE sampleTime IN ('"+"','".join(df.sampleTime.values)+"');"
    alreadyExists = pd.read_sql_query(cmd, engine)
    df['sampleTime'] = pd.to_datetime(df['sampleTime'])
    alreadyExists['sampleTime'] = pd.to_datetime(alreadyExists['sampleTime'])
    
    #now merge to create environ_id column. rows with NaNs for 
    #their environ_id will be unique, and should be added to the DB:
    df = df.merge(alreadyExists, how='outer', on='sampleTime')
    
    #keep only the new entries:
    df = df[pd.isnull(df['environ_id'])]

    #drop duplicates with the same sampleTime if they existed in the log file:
    df.drop_duplicates(subset='sampleTime', inplace=True)
    
    #now append the data to the environ table:
    print('{0}: Added {1} rows to the DB.'.format(date, len(df)))
    if len(df) > 0:
        df.to_sql('environ', engine, if_exists='append', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='addEnviron: a routine to parse the ' +
                    'environmental logs for temperature ' +
                    'and pressure information and write ' +
                    'that information to the DB.')
    parser.add_argument(
        'date',
        help='The date of the logs to restore in yymmdd format')
    if len(sys.argv) > 2:
        print('use the command')
        print('python addEnviron.py date')
        sys.exit(2)

    args = parser.parse_args()

    addEnviron(args.date)
 