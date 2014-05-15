#!/usr/bin/env python

"""
Created on 2014-05-14T15:44:41
"""

__author__ = "Matt Giguere (github: @mattgiguere)"
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"
__version__ = '0.0.1'

from __future__ import division, print_function
import pymysql
from __future__ import print_function
import subprocess
import sys

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


def create_chidb(arg1, arg2):
    """PURPOSE: To create the CHIRON MySQL database."""

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

    #The new tables in the database:
    new_tables = ['observations',
                  'ccdsections',
                  'environment',
                  'weather',
                  'seeing',
                  'exposuremeter',
                  'reduction']

    table_dict = {}

    #observations table:
    table_dict[new_tables[0]] = {
        'observation_id': 'INT AUTO_INCREMENT PRIMARY KEY',
        'object_id': 'INT',
        'simple': 'char(1)',
        'bitpix': 'FLOAT',
        'naxis': 'INT',
        'naxis1': 'INT',
        'naxis2': 'INT',
        'extend': 'char(1)',
        'bzero': 'INT',
        'bscale': 'INT',
        'object': 'varchar(60)',
        'observer': 'varchar(60)',
        'propid': 'INT',
        'obsid': 'varchar(60)',
        'imagetyp': 'varchar(60)',
        'ccdsum': 'varchar(60)',
        'roireq': 'varchar(60)',
        'utshut': 'varchar(60)',
        'date': 'varchar(60)',
        'nampsyx': 'varchar(60)',
        'amplist': 'varchar(60)',
        'detector': 'varchar(60)',
        'fpa': 'varchar(60)',
        'rexptime': 'FLOAT',
        'exptime': 'FLOAT',
        'texptime': 'FLOAT',
        'darktime': 'FLOAT',
        'nimages': 'INT',
        'dheinf': 'varchar(60)',
        'dhefirm': 'varchar(60)',
        'speedmod': 'varchar(60)',
        'geommod': 'varchar(60)',
        'pixtime': 'FLOAT',
        'powstat': 'FLOAT',
        'fpgafirm': 'FLOAT',
        'slot00': 'varchar(60)',
        'slot01': 'varchar(60)',
        'slot02': 'varchar(60)',
        'slot03': 'varchar(60)',
        'slot04': 'varchar(60)',
        'slot07': 'varchar(60)',
        'slot02': 'varchar(60)',
        'panid': 'varchar(60)',
        'comment': 'varchar(60)',
        'dhsid': 'varchar(60)',
        'deckpos': 'FLOAT',
        'decker': 'varchar(60)',
        'focus': 'FLOAT',
        'maxexp': 'INT',
        'pmhv': 'varchar(60)',
        'complamp': 'varchar(60)',
        'iodcell': 'varchar(60)',
        'observat': 'varchar(60)',
        'telescop': 'varchar(60)',
        'date-obs': 'varchar(60)',
        'ut': 'varchar(60)',
        'ra': 'varchar(60)',
        'dec': 'varchar(60)',
        'epoch': 'FLOAT',
        'alt': 'FLOAT',
        'ha': 'FLOAT',
        'st': 'varchar(60)',
        'zd': 'FLOAT',
        'airmass': 'FLOAT'}

    #CCD Sections Table
    table_dict[new_tables[1]] = {
        'observation_id': 'INT',
        'tsec22': 'varchar(60)',
        'asec22': 'varchar(60)',
        'csec22': 'varchar(60)',
        'bsec22': 'varchar(60)',
        'dsec22': 'varchar(60)',
        'scsec22': 'varchar(60)',
        'tsec12': 'varchar(60)',
        'asec12': 'varchar(60)',
        'csec12': 'varchar(60)',
        'bsec12': 'varchar(60)',
        'dsec12': 'varchar(60)',
        'scsec12': 'varchar(60)',
        'tsec11': 'varchar(60)',
        'asec11': 'varchar(60)',
        'csec11': 'varchar(60)',
        'bsec11': 'varchar(60)',
        'dsec11': 'varchar(60)',
        'scsec11': 'varchar(60)',
        'tsec21': 'varchar(60)',
        'asec21': 'varchar(60)',
        'csec21': 'varchar(60)',
        'bsec21': 'varchar(60)',
        'dsec21': 'varchar(60)',
        'scsec21': 'varchar(60)',
        'gain11': 'FLOAT',
        'ron11': 'FLOAT',
        'gain12': 'FLOAT',
        'ron12': 'FLOAT',
        'gain21': 'FLOAT',
        'ron21': 'FLOAT',
        'gain22': 'FLOAT',
        'ron22': 'FLOAT'}

    cur.execute("CREATE TABLE ")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('')
        print('python create_chidb.py arg1 arg2')
        print('')
        sys.exit(2)
    elif len(sys.argv) != 3:
        print('use the command')
        print('python filename.py arg1 arg2')
        sys.exit(2)

    arg1 = int(sys.argv[2])
    arg2 = str(sys.argv[1])

    create_chidb(arg1, arg2)
