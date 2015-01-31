#!/usr/bin/env python

"""
Created on 2015-01-31T17:24:25
"""

from __future__ import division, print_function
import argparse

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
    To add environmental information to the CHIRON DB. 

    date: the date in yymmdd format

    example from the command line:
        python addEnviron 150131
    """
    #filenames for the four environmental logs:
    instfn = '/tous/mir7/logs/temps/insttemp/insttemp'+date+'.log'
    htfn =  '/tous/mir7/logs/temps/heater/heater'+date+'.log'
    ctfn = '/tous/mir7/logs/temps/chitemp/chitemp'+date+'.log'
    dtfn = '/tous/mir7/logs/temps/dettemp/dettemp'+date+'.log'

    #restore the insttemp log:
    df_in = pd.read_table(instfn, sep='\s', engine='python', header=None)
    df_in.columns = ['sampleTime', 'jnk1', 'gratingTemp', 'jnk2', 'tableCenterTemp', 'jnk3', 'enclosureTemp', 'jnk4',
                  'iodineCellTemp', 'jnk5', 'enclosureSetpoint', 'jnk6', 'iodineCellSetpoint', 'jnk7',
                  'enclosureTemp2', 'jnk8', 'tableTempLow', 'jnk9', 'structureTemp', 'jnk10', 'instrumentSetpoint',
                  'jnk11', 'instrumentTemp', 'jnk12', 'coudeTemp']
    df = df_in[['sampleTime', 'gratingTemp', 'tableCenterTemp', 'enclosureTemp',
                  'iodineCellTemp', 'enclosureSetpoint', 'iodineCellSetpoint',
                  'enclosureTemp2', 'tableTempLow', 'structureTemp', 'instrumentSetpoint',
                  'instrumentTemp', 'coudeTemp']]

    #restore and merge the heater log:
    ht_in = pd.read_table(htfn, sep='\s', engine='python', header=None)
    ht_in.columns = ['sampleTime', 'jnk1', 'heaterSetpoint']
    ht = ht_in[['sampleTime', 'heaterSetpoint']]
    df = df.merge(ht, on='sampleTime', how='left')

    #restore and merge the chitemp log:
    ct_in = pd.read_table(ctfn, sep='\s', engine='python', header=None)
    ct_in.columns = ['sampleTime', 'jnk', 'barometer', 'jnk', 'echellePressure']
    ct = ct_in[['sampleTime', 'barometer', 'echellePressure']]
    df = df.merge(ct, on='sampleTime')

    #restore and merge the dettemp log:
    dt_in = pd.read_table(dtfn, sep='\s', engine='python', header=None)
    dt_in.columns = ['sampleTime', 'jnk1', 'ccdTemp', 'jnk2', 'neckTemp', 'jnk3', 'ccdSetpoint']
    dt = dt_in[['sampleTime', 'ccdTemp', 'neckTemp', 'ccdSetpoint']]
    df = df.merge(dt, on='sampleTime')

    #add an empty column for the timestamp of when the 
    #entry was added to the DB:
    df['dateAdded'] = None
    #connect to the CHIRON DB:
    engine = ccdb.connectChironDB()
    #now append the data to the environ table:
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
 