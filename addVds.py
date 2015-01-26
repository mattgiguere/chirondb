#!/usr/bin/env python

"""
Created on 2015-01-25T19:37:27
"""

from __future__ import division, print_function
import sys
import argparse

import pandas as pd
import idlToPandas.idlToPandas as itp
from pyutil import connectChironDB as ccdb
import subprocess
import re

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Production"
__version__ = '0.0.1'


def addVds(star, tag):
    """
    PURPOSE: To add all the vd files for a given tag and star name to the DB.
    """

    #list all files 
    cmd = "ls -1d /tous/mir7/vel/vd"+star+"/vd"+tag+"*"
    filestring = subprocess.check_output(cmd, shell=True)
    files = filestring.split('\n')
    files = files
    
    #loop through files, restoring each one and adding it
    #to the database:
    for idx, fname in enumerate(files):
        print('{0} of {1}: {2}'.format(idx, len(files), fname))
        #restore file and write it 
        #to a pandas dataFrame:
        vd = itp.idlToPandas(fname)
        
        #now convert arrays within DF to separate
        #columns to be written to the DB:
        vd['WCOF0'] = [x[0] for x in vd['WCOF'].values]
        vd['WCOF1'] = [x[1] for x in vd['WCOF'].values]
        vd['WCOF2'] = [x[2] for x in vd['WCOF'].values]
        vd['WCOF3'] = [x[3] for x in vd['WCOF'].values]

        vd['ICOF0'] = [x[0] for x in vd['ICOF'].values]
        vd['ICOF1'] = [x[1] for x in vd['ICOF'].values]
        vd['ICOF2'] = [x[2] for x in vd['ICOF'].values]
        vd['ICOF3'] = [x[3] for x in vd['ICOF'].values]

        vd['SCOF0'] = [x[0] for x in vd['SCOF'].values]
        vd['SCOF1'] = [x[1] for x in vd['SCOF'].values]
        vd['SCOF2'] = [x[2] for x in vd['SCOF'].values]
        vd['SCOF3'] = [x[3] for x in vd['SCOF'].values]

        vd['IPARAM00'] = [x[0] for x in vd['IPARAM'].values]
        vd['IPARAM01'] = [x[1] for x in vd['IPARAM'].values]
        vd['IPARAM02'] = [x[2] for x in vd['IPARAM'].values]
        vd['IPARAM03'] = [x[3] for x in vd['IPARAM'].values]
        vd['IPARAM04'] = [x[4] for x in vd['IPARAM'].values]
        vd['IPARAM05'] = [x[5] for x in vd['IPARAM'].values]
        vd['IPARAM06'] = [x[6] for x in vd['IPARAM'].values]
        vd['IPARAM07'] = [x[7] for x in vd['IPARAM'].values]
        vd['IPARAM08'] = [x[8] for x in vd['IPARAM'].values]
        vd['IPARAM09'] = [x[9] for x in vd['IPARAM'].values]
        vd['IPARAM10'] = [x[10] for x in vd['IPARAM'].values]
        vd['IPARAM11'] = [x[11] for x in vd['IPARAM'].values]
        vd['IPARAM12'] = [x[12] for x in vd['IPARAM'].values]
        vd['IPARAM13'] = [x[13] for x in vd['IPARAM'].values]
        vd['IPARAM14'] = [x[14] for x in vd['IPARAM'].values]
        vd['IPARAM15'] = [x[15] for x in vd['IPARAM'].values]
        vd['IPARAM16'] = [x[16] for x in vd['IPARAM'].values]
        vd['IPARAM17'] = [x[17] for x in vd['IPARAM'].values]
        vd['IPARAM18'] = [x[18] for x in vd['IPARAM'].values]
        vd['IPARAM19'] = [x[19] for x in vd['IPARAM'].values]

        #delete array columns
        vd = vd.drop('WCOF', 1)
        vd = vd.drop('ICOF', 1)
        vd = vd.drop('SCOF', 1)
        vd = vd.drop('IPARAM', 1)

        #create the vd_id. This will be auto-indexed if 
        #set to None
        vd['vd_id'] = None
        #create other columns
        vd['filename'] = fname
        vd['tag'] = tag

        #extract the obnm from the filename (e.g. achi131009.2137)
        #this will be used to get the observation_id from the 
        #observations table.
        obnm = re.search(r'achi[0-9]{6}.[0-9]{4}', fname).group(0)

        #now connect to the CHIRON MySQL DB, and get the observation_id
        #associated with this observation.
        engine = ccdb.connectChironDB()
        cmd = "SELECT observation_id FROM observations where obnm = '"+obnm+"';"
        vd['observation_id'] = pd.read_sql_query(cmd, engine).values[0][0]

        #lastly, write the results to the DB:
        vd.to_sql('vds', engine, if_exists='append', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A routine to read in vd IDL structures ' +
                    'and write them to the chirondb. ' +
                    'example: ' +
                    'python addVds.py 10700 a')
    parser.add_argument(
        'star',
        help='The name of the target to add to the DB.')
    parser.add_argument(
        'tag',
        help='the run tag to use (e.g. a)')
    if len(sys.argv) > 3:
        print('use the command')
        print('python addVds.py star tag')
        sys.exit(2)

    args = parser.parse_args()

    addVds(args.star, args.tag)
 