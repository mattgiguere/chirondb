#!/usr/bin/env python

"""
Created on 2015-02-01T13:53:47
"""

from __future__ import division, print_function
import sys
import argparse
import datetime
import os

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
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

def driveDates(date_beg, date_end, logtodb='environ'):
    
    if date_beg < 9e5:
        date_beg += 2e6
        date_begs = str(date_beg)
        dtBeg = datetime.date(date_begs[0:4], date_begs[4:6], date_begs[6:8])
    
    if date_end < 9e5:
        date_end += 2e6
        date_ends = str(date_eng)
        dtEnd = datetime.date(date_ends[0:4], date_ends[4:6], date_ends[6:8])
    
    ndates = dtEnd - dtBeg
        
    for i in range(ndates.days):
        
        #create a datetime object for the current iteration:
        dtCur = dtBeg + datetime.timedelta(days=i)
        print('Now on date: {}'.format(dtCur))
        
        if logtodb == 'environ':
            from addEnviron import addEnviron
            #change the datetime object to a string in yymmdd format:
            dtymd = str(dtCur).replace('-', '')[2::]
            
            #now do a quick file test to make sure a log exists
            #before trying to add it to the DB:
            logpath = '/tous/mir7/logs/temps/insttemp/'
            filenm = 'insttemp'+dtymd+'.log'
            if os.path.isfile(logpath+filenm):
                addEnviron(dtymd)
            

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
        print('python filename.py tablenum columnnum')
        sys.exit(2)

    args = parser.parse_args()

    driveDates(int(args.arg1), args.arg2)
 