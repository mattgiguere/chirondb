#!/usr/bin/env python

"""
Created on 2014-05-14T15:44:41
"""

from __future__ import division, print_function
import pymysql
import subprocess
import sys
import argparse
from collections import OrderedDict

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
    observationsTable = OrderedDict()
    observationsTable['observation_id'] = 'INT AUTO_INCREMENT PRIMARY KEY'
    observationsTable['object_id'] = 'INT'
    observationsTable['simple'] = 'char(1)'
    observationsTable['bitpix'] = 'FLOAT'
    observationsTable['naxis'] = 'INT'
    observationsTable['naxis1'] = 'INT'
    observationsTable['naxis2'] = 'INT'
    observationsTable['extend'] = 'char(1)'
    observationsTable['bzero'] = 'INT'
    observationsTable['bscale'] = 'INT'
    observationsTable['object'] = 'varchar(60)'
    observationsTable['observer'] = 'varchar(60)'
    observationsTable['propid'] = 'INT'
    observationsTable['obsid'] = 'varchar(60)'
    observationsTable['imagetyp'] = 'varchar(60)'
    observationsTable['ccdsum'] = 'varchar(60)'
    observationsTable['roireq'] = 'varchar(60)'
    observationsTable['utshut'] = 'varchar(60)'
    observationsTable['date'] = 'varchar(60)'
    observationsTable['nampsyx'] = 'varchar(60)'
    observationsTable['amplist'] = 'varchar(60)'
    observationsTable['detector'] = 'varchar(60)'
    observationsTable['fpa'] = 'varchar(60)'
    observationsTable['rexptime'] = 'FLOAT'
    observationsTable['exptime'] = 'FLOAT'
    observationsTable['texptime'] = 'FLOAT'
    observationsTable['darktime'] = 'FLOAT'
    observationsTable['nimages'] = 'INT'
    observationsTable['dheinf'] = 'varchar(60)'
    observationsTable['dhefirm'] = 'varchar(60)'
    observationsTable['speedmod'] = 'varchar(60)'
    observationsTable['geommod'] = 'varchar(60)'
    observationsTable['pixtime'] = 'FLOAT'
    observationsTable['powstat'] = 'FLOAT'
    observationsTable['fpgafirm'] = 'FLOAT'
    observationsTable['slot00'] = 'varchar(60)'
    observationsTable['slot01'] = 'varchar(60)'
    observationsTable['slot02'] = 'varchar(60)'
    observationsTable['slot03'] = 'varchar(60)'
    observationsTable['slot04'] = 'varchar(60)'
    observationsTable['slot07'] = 'varchar(60)'
    observationsTable['slot02'] = 'varchar(60)'
    observationsTable['panid'] = 'varchar(60)'
    observationsTable['comment'] = 'varchar(60)'
    observationsTable['dhsid'] = 'varchar(60)'
    observationsTable['deckpos'] = 'FLOAT'
    observationsTable['decker'] = 'varchar(60)'
    observationsTable['focus'] = 'FLOAT'
    observationsTable['maxexp'] = 'INT'
    observationsTable['pmhv'] = 'varchar(60)'
    observationsTable['complamp'] = 'varchar(60)'
    observationsTable['iodcell'] = 'varchar(60)'
    observationsTable['observat'] = 'varchar(60)'
    observationsTable['telescop'] = 'varchar(60)'
    observationsTable['date_obs'] = 'varchar(60)'
    observationsTable['ut'] = 'varchar(60)'
    observationsTable['obs_ra'] = 'varchar(60)'
    observationsTable['obs_dec'] = 'varchar(60)'
    observationsTable['epoch'] = 'FLOAT'
    observationsTable['alt'] = 'FLOAT'
    observationsTable['ha'] = 'FLOAT'
    observationsTable['st'] = 'varchar(60)'
    observationsTable['zd'] = 'FLOAT'
    observationsTable['airmass'] = 'FLOAT'
    table_dict[table_names[0]] = observationsTable

    #CCD Sections Table
    ccdSectionsTable = OrderedDict()
    ccdSectionsTable['observation_id'] = 'INT'
    ccdSectionsTable['tsec22'] = 'varchar(60)'
    ccdSectionsTable['asec22'] = 'varchar(60)'
    ccdSectionsTable['csec22'] = 'varchar(60)'
    ccdSectionsTable['bsec22'] = 'varchar(60)'
    ccdSectionsTable['dsec22'] = 'varchar(60)'
    ccdSectionsTable['scsec22'] = 'varchar(60)'
    ccdSectionsTable['tsec12'] = 'varchar(60)'
    ccdSectionsTable['asec12'] = 'varchar(60)'
    ccdSectionsTable['csec12'] = 'varchar(60)'
    ccdSectionsTable['bsec12'] = 'varchar(60)'
    ccdSectionsTable['dsec12'] = 'varchar(60)'
    ccdSectionsTable['scsec12'] = 'varchar(60)'
    ccdSectionsTable['tsec11'] = 'varchar(60)'
    ccdSectionsTable['asec11'] = 'varchar(60)'
    ccdSectionsTable['csec11'] = 'varchar(60)'
    ccdSectionsTable['bsec11'] = 'varchar(60)'
    ccdSectionsTable['dsec11'] = 'varchar(60)'
    ccdSectionsTable['scsec11'] = 'varchar(60)'
    ccdSectionsTable['tsec21'] = 'varchar(60)'
    ccdSectionsTable['asec21'] = 'varchar(60)'
    ccdSectionsTable['csec21'] = 'varchar(60)'
    ccdSectionsTable['bsec21'] = 'varchar(60)'
    ccdSectionsTable['dsec21'] = 'varchar(60)'
    ccdSectionsTable['scsec21'] = 'varchar(60)'
    ccdSectionsTable['gain11'] = 'FLOAT'
    ccdSectionsTable['ron11'] = 'FLOAT'
    ccdSectionsTable['gain12'] = 'FLOAT'
    ccdSectionsTable['ron12'] = 'FLOAT'
    ccdSectionsTable['gain21'] = 'FLOAT'
    ccdSectionsTable['ron21'] = 'FLOAT'
    ccdSectionsTable['gain22'] = 'FLOAT'
    ccdSectionsTable['ron22'] = 'FLOAT'
    table_dict[table_names[1]] = ccdSectionsTable

    #Environment Table
    environmentTable = OrderedDict()
    environmentTable['observation_id'] = 'INT'
    environmentTable['ccdtemp'] = 'FLOAT'
    environmentTable['necktemp'] = 'FLOAT'
    environmentTable['tempgrat'] = 'FLOAT'
    environmentTable['temptlow'] = 'FLOAT'
    environmentTable['temptcen'] = 'FLOAT'
    environmentTable['tempstru'] = 'FLOAT'
    environmentTable['tempencl'] = 'FLOAT'
    environmentTable['tempcoud'] = 'FLOAT'
    environmentTable['tempinst'] = 'FLOAT'
    environmentTable['tempiodin'] = 'FLOAT'
    environmentTable['dewpress'] = 'FLOAT'
    environmentTable['echpress'] = 'FLOAT'
    environmentTable['baromete'] = 'FLOAT'
    table_dict[table_names[2]] = environmentTable

    #Weather Table
    weatherTable = OrderedDict()
    weatherTable['observation_id'] = 'INT'
    weatherTable['wthr_id'] = 'INT'
    weatherTable['weatime'] = 'varchar(60)'
    weatherTable['weatimejd'] = 'FLOAT'
    weatherTable['outtemp'] = 'FLOAT'
    weatherTable['outhum'] = 'FLOAT'
    weatherTable['outpress'] = 'FLOAT'
    weatherTable['wndspeed'] = 'FLOAT'
    weatherTable['wnddir'] = 'FLOAT'
    table_dict[table_names[3]] = weatherTable

    #Seeing Table
    seeingTable = OrderedDict()
    seeingTable['observation_id'] = 'INT'
    seeingTable['see_id'] = 'INT'
    seeingTable['seetime'] = 'varchar(60)'
    seeingTable['seetimejd'] = 'FLOAT'
    seeingTable['seeing'] = 'FLOAT'
    seeingTable['sairmass'] = 'FLOAT'
    table_dict[table_names[4]] = seeingTable

    #Exposure Meter Table
    exposureMeterTable = OrderedDict()
    exposureMeterTable['observation_id'] = 'INT'
    exposureMeterTable['em_id'] = 'INT'
    exposureMeterTable['emtimopn'] = 'varchar(60)'
    exposureMeterTable['emtimcls'] = 'varchar(60)'
    exposureMeterTable['emnumsmp'] = 'INT'
    exposureMeterTable['emavg'] = 'FLOAT'
    exposureMeterTable['amavgsq'] = 'FLOAT'
    exposureMeterTable['emprdsum'] = 'FLOAT'
    exposureMeterTable['emnetint'] = 'FLOAT'
    exposureMeterTable['emmnwob'] = 'varchar(60)'
    exposureMeterTable['emmnwb'] = 'varchar(60)'
    exposureMeterTable['thres'] = 'FLOAT'
    exposureMeterTable['emtimopnjd'] = 'FLOAT'
    exposureMeterTable['emmnwobjd'] = 'FLOAT'
    exposureMeterTable['emmnwbjd'] = 'FLOAT'
    table_dict[table_names[5]] = exposureMeterTable

    #Reduction Table
    reductionTable = OrderedDict()
    reductionTable['observation_id'] = 'INT'
    reductionTable['red_id'] = 'INT'
    reductionTable['resolutn'] = 'FLOAT'
    reductionTable['thidnlin'] = 'INT'
    reductionTable['tharfnam'] = 'varchar(60)'
    reductionTable['snrbp5500'] = 'FLOAT'
    table_dict[table_names[6]] = reductionTable

    return table_names, table_dict


def createTable(table_name, table_dict):
    currentTable = table_dict[table_name]
    currentKeys = currentTable.keys()

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
    cur.execute("SHOW TABLES")
    preExistingTables = cur.fetchall()
    if (not((table_name,) in preExistingTables)):
        cur.execute("CREATE TABLE " + table_name +
                    " (" + currentKeys[0] + " " +
                    currentTable[currentKeys[0]]+")")

    cur.execute("DESCRIBE "+table_name)
    preexistingKeys = [x[0] for x in cur.fetchall()]
    for key in currentKeys:
        print('***************************************')
        print(key)
        if key in preexistingKeys:
            print('***WARNING! KEY ALREADY EXISTED!***')
        else:
            print('Now adding '+key)
            cur.execute("ALTER TABLE " + table_name + " ADD (" +
                        key + ' ' + currentTable[key]+')')


def removeTableFields(table_name, table_dict):
    currentTable = table_dict[table_name]
    currentKeys = currentTable.keys()

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
    cur.execute("SHOW TABLES")
    preExistingTables = cur.fetchall()
    if (not((table_name,) in preExistingTables)):
        cur.execute("CREATE TABLE " + table_name +
                    " (" + currentKeys[0] + " " +
                    currentTable[currentKeys[0]]+")")

    cur.execute("DESCRIBE "+table_name)
    preexistingKeys = [x[0] for x in cur.fetchall()]
    for key in currentKeys:
        print('***************************************')
        print(key)
        if key in preexistingKeys:
            print('Now removing '+key)
            cur.execute("ALTER TABLE " + table_name + " DROP " + key)
        else:
            print('***WARNING! KEY DID NOT EXIST!***')


def createDB():
    table_names, table_dict = getTables()
    for tName in table_names:
        print('===============================')
        print('Now making ' + tName + ' table.')
        print('===============================')
        createTable(tName, table_dict)


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
        createTable(table_names[args.tablenum], table_dict)
