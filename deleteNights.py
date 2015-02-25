#!/usr/bin/env python

"""
Created on 2015-01-04T13:59:13
"""

from __future__ import division, print_function
import sys
import argparse

try:
    import pandas as pd
except ImportError:
    print('You need pandas installed')
    sys.exit(1)

try:
    import pyutil.connectChironDB as ccdb
except ImportError:
    print('You need Matts pyutil installed')
    sys.exit(1)

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.2'


def deleteNights(night, execute=False):
    """
    PURPOSE: To delete all rows from all tables that contain
    information from the night of interest.

    Input:
    ------
    night: The night of interest, in yymmdd form.

    Optional Input:
    ---------------
    execute: If set as False, the code will execute a SELECT COUNT(*)
    and print the number of rows in each table instead of
    executing the DELETE statement. Set to True to actually
    DELETE the rows in all tables for the night.

    Example:
    --------
    python deleteNights.py 140725 --execute

    """

    #read in the table names to delete all entries from:
    tbls = pd.read_csv('tables/tableList.txt')

    #make sure the date is a string:
    night = str(night)
    conn = ccdb.connectChironDB(legacy=True)
    cur = conn.cursor()
    for i in range(len(tbls)):
        iname = tbls.loc[i, 'tableName']
        if iname != 'observations' and iname != 'spectra':
            if execute is False:
                cmd = 'SELECT COUNT(*) FROM '+iname
                print('Table name is {0}'.format(iname))
            else:
                cmd = 'DELETE FROM '+iname
            cmd += ' WHERE observation_id in '
            cmd += '(SELECT observation_id FROM observations '
            cmd += "WHERE MID(rawfilename, 11, 6)='"+night+"');"
            #print(cmd)
            cur.execute(cmd)
            counts = cur.fetchall()
            print(counts)

            #commit the changes to the database:
            conn.commit()

    #lastly, delete from the observations table:
    if execute is False:
        cmd = 'SELECT COUNT(*) FROM observations '
        print('Table name is observations')
    else:
        cmd = 'DELETE FROM observations '
    cmd += "WHERE MID(rawfilename, 11, 6)='"+night+"';"
    #print(cmd)
    cur.execute(cmd)
    counts = cur.fetchall()
    print(counts)

    #commit the changes to the database:
    conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'night',
        help='This argument specifies which night to delete. ' +
             'Needs to be in yymmdd format.')
    parser.add_argument(
        '-e', '--execute', action="store_true",
        help='The execute argument specifies whether or not the code should ' +
             'just be tested. Default is False. Set to True to execute ' +
             'the DELETE command.')
    if len(sys.argv) > 3:
        print('use the command')
        print('python deleteNights.py night --execute')
        sys.exit(2)

    args = parser.parse_args()
    print('args.execute is ')
    print(args.execute)

    deleteNights(str(args.night), execute=args.execute)
