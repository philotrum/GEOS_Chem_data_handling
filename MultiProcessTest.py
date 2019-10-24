#!/usr/bin/env python
import os
from multiprocessing import Pool
import datetime as dt

startTime = dt.datetime.now()

def processData(inDate):
    
    for ext in extensions:    
        
        filename = '/home/admin/tmp/GEOSFP.' + inDate + '.' + ext + '.025x03125.nc'
        if (os.path.isfile(filename)):
            print('Processing ' + filename)
            processedFilename = '/home/admin/tmp/GEOSFP.' + inDate + '.' + ext + '.025x03125' + '.AU.nc'
            if (not os.path.isfile(processedFilename)):
                commandline = 'ncks -a -d lat,-46.0,-6.0 -d lon,110.0,155.0 ' + filename + ' ' + processedFilename
                os.system(commandline)
            else:
                print('No need to process ' + processedFilename + ' as it already exists.')
        else:
            print(filename + ' does not exist')
        
extensions = ['A1', 'A3cld', 'A3dyn', 'A3mstC' , 'A3mstE', 'I3']

year = '2018'
month = '09'

missingFiles = []
corruptFiles = [] 


daysInMonth = 11
daysToProcess = [year + month + str(day).zfill(2) for day in range(1, daysInMonth +1)]

with Pool() as p:
    p.map(processData, daysToProcess)

totalTime = dt.datetime.now() - startTime
print('Total time: ' + str(totalTime))