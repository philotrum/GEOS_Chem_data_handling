#!/usr/bin/env python

import sys, os

date = sys.argv[1]

year = date[:4]
month = date[4:6]

commandline =  'scp *' + date + '*.AU* gck574@raijin.nci.org.au:/g/data3/m19/geos-chem/data/GEOS_0.25x0.3125_AU/GEOS_FP/' 
commandline = commandline + year + '/' + month + '/'

os.system(commandline)