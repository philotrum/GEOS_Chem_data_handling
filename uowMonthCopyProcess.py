#!/usr/bin/env python

import sys, os
from ftplib import FTP
import urllib
import threading
import datetime as dt

def getData_ftp(inDate, inExtensions):
    
    ftp=FTP('geoschemdata.computecanada.ca/')
    ftp.login()
    ftp.cwd('GEOS_0.25x0.3125/GEOS_FP/' + year + '/' + month)
    
    for ext in inExtensions:
        
        try:
            filename = 'GEOSFP.' + inDate + '.' + ext + '.025x03125.nc'
            if (not os.path.isfile(filename)):
                localFile = open(filename, 'wb')
                print('Copying ' + filename)
                ftp.retrbinary('RETR ' + filename, localFile.write, 1024)
            else:
                print filename + ' already exists. No need to copy.'
        except:
            print filename + ' failed to copy from the remote server.'
    
    ftp.quit()
    ftp = None
    
def getData_html(inDate, inExtensions):
    
    url = 'http://geoschemdata.computecanada.ca/GEOS_0.25x0.3125/GEOS_FP/' + year + '/' + month + '/'
    
    for ext in inExtensions:
        
        try:
            filename = 'GEOSFP.' + inDate + '.' + ext + '.025x03125.nc'
            print 'Filename: ' + filename
            remoteFilename = url + filename
            if (not os.path.isfile(filename)):
                urllib.urlretrieve(remoteFilename, filename)
            else:
                print filename + ' already exists. No need to copy.'
        except:
            print filename + ' failed to copy from the remote server.'
    
def processData(inDate, inExtensions):
    
    for ext in inExtensions:
    
        try:
            filename = '/home/admin/tmp/GEOSFP.' + inDate + '.' + ext + '.025x03125.nc'
            print 'Processing ' + filename
            processedFilename = '/home/admin/tmp/GEOSFP.' + inDate + '.' + ext + '.025x03125' + '.AU.nc'
            if (not os.path.isfile(processedFilename)):
                pass
                commandline = 'ncks -a -d lat,-46.0,-6.0 -d lon,110.0,155.0 ' + filename + ' ' + processedFilename
                os.system(commandline)
            else:
                print 'No need to process ' + processedFilename + ' as it already exists.'
        except:
            print filename + ' does not exist'

# Start of program
startDate = sys.argv[1]
extensions = ['A1', 'A3cld', 'A3dyn', 'A3mstC' , 'A3mstE', 'I3']
maxNumThreads = 6

year = startDate[:4]
month = startDate[4:6]

daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
if (int(year) % 4 == 0):
    daysInMonths[1] = 29
    
start = dt.datetime.now()
print start 

daysInMonth = daysInMonths[int(month) - 1]
startDay = 0
numIters = int(daysInMonth / maxNumThreads)
if (daysInMonth % maxNumThreads > 0):
    numIters += 1

for i in range(numIters):
    
    # Create and run threads for parallel downloads
    threads = []
    finishDay = startDay + maxNumThreads
    if (finishDay > daysInMonth):
        finishDay = daysInMonth
    
    for i in range(startDay, finishDay):
        startDay += 1
        date = year + month + str(startDay).zfill(2)
        print date
        t = threading.Thread(target = getData_html, args = (date, extensions,))
        threads.append(t)
    
    for x in threads:
        x.start()
        
    for x in threads:
        x.join()
    
finish = dt.datetime.now()
totalTime = finish - start
print str(totalTime)

threads = None

threads = []
day = 1
for i in range(daysInMonth):
    
    date = year + month + str(day).zfill(2)
    t = threading.Thread(target = processData, args = (date, extensions,))
    threads.append(t)
    day += 1
    
for x in threads:
    x.start()
    
for x in threads:
    x.join()
    
for day in range(daysInMonth):
    
    date = year + month + str(day + 1).zfill(2)
    commandline =  'scp *' + date + '*.AU* gck574@raijin.nci.org.au:/g/data3/m19/geos-chem/data/GEOS_0.25x0.3125_AU/GEOS_FP/' 
    commandline = commandline + year + '/' + month + '/'
    os.system(commandline)