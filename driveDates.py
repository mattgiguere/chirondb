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

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'

def driveDates(date_beg, date_end, logtodb='environ'):
    
    if date_beg < 9e5:
        date_beg += 20000000
        date_begs = str(date_beg)
        dtBeg = datetime.date(int(date_begs[0:4]), int(date_begs[4:6]), int(date_begs[6:8]))
    
    if date_end < 9e5:
        date_end += 20000000
        date_ends = str(date_end)
        dtEnd = datetime.date(int(date_ends[0:4]), int(date_ends[4:6]), int(date_ends[6:8]))
    
    ndates = dtEnd - dtBeg
        
    for i in range(ndates.days+1):
        
        #create a datetime object for the current iteration:
        dtCur = dtBeg + datetime.timedelta(days=i)
        #print('Now on date: {}'.format(dtCur))
        
        if logtodb == 'environ':
            try:
                from addEnviron import addEnviron
            except ImportError:
                print('You need addEnviron installed')
                print('https://github.com/mattgiguere/chirondb')
                sys.exit(1)

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
        'date_beg',
        help='The beginning date of the date range in yymmdd format')
    parser.add_argument(
        'date_end',
        help='The ending date of the date range in yymmdd format ')
    parser.add_argument(
        '--logtodb',
        help='Optional: the log to drive to the DB. Current options are: environ.')
    if len(sys.argv) > 5:
        print('use the command')
        print('python driveDates.py date_beg date_end --logtodb dbTableName')
        print('Example: python driveDates.py 141021 150131 --logtodb environ')
        sys.exit(2)

    args = parser.parse_args()

    if args.logtodb:
        args.logtodb = args.logtodb
    else:
        args.logtodb = 'environ'

    driveDates(int(args.date_beg), int(args.date_end), logtodb=args.logtodb)
 