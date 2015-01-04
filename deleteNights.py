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
    import matplotlib.pyplot as plt
    got_mpl = True
except ImportError:
    print('You need matplotlib installed to get a plot')
    got_mpl = False

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'

params = {
    #'backend': 'png',
    'axes.linewidth': 1.5,
    'axes.labelsize': 24,
    'axes.font': 'sans-serif',
    'axes.fontweight': 'bold',
    'text.fontsize': 22,
    'legend.fontsize': 14,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'text.usetex': False,
    'font.family': 'Arial Black'
}
plt.rcParams.update(params)


def deleteNights(arg1, arg2):
    """
    PURPOSE: To delete all rows from all tables that contain 
    information from the night of interest.
    
    Input:
    ------
    night: The night of interest, in yymmdd form.
    
    Optional Input:
    ---------------
    test: If set as True, the code will execute a SELECT COUNT(*)
    and print the number of rows in each table instead of 
    executing the DELETE statement. Set T
    
    """

    #read in the table names to delete all entries from:
    tbls = pd.read_csv('tables/tableListFull.txt')

    #make sure the date is a string:
    night = str(night)
    cur = conn.cursor()
    for i in range(len(tbls)):
        iname = tbls.loc[i, 'tableName']
        if iname != 'observations' and iname != 'spectra':
            if test is True:
                cmd = 'SELECT COUNT(*) FROM '+iname
                print('Table name is {0}'.format(iname))
            else:
                cmd = 'DELETE FROM '+iname
            cmd += ' WHERE observation_id in '
            cmd += '(SELECT observation_id FROM observations '
            cmd +="WHERE MID(rawfilename, 11, 6)='"+night+"');"
            #print(cmd)
            cur.execute(cmd)
            counts = cur.fetchall()
            print(counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'arg1',
        help='This argument does something.')
    parser.add_argument(
        'arg2',
        help='This argument does something else. By specifying ' +
             'the "nargs=>" makes this argument not required.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python deleteNights.py arg1 arg2')
        sys.exit(2)

    args = parser.parse_args()

    deleteNights(int(args.arg1), args.arg2)
 