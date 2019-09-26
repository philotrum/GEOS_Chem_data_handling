#!/usr/bin/env python

# This file copies global GEOSChem input files from the ComputeCanada server, extracts the data for 
# the Australian region into another file, and then copies the files to NCI for use.

# Usage:
#   python uowCopyProcess yyyymmdd    - copies and processes the data for the specified day
#   python uowCopyProcess yyyymm      - copies and processes all data for the entire month specified.

import sys, os
from ftplib import FTP
import urllib
import threading
import datetime as dt
import paramiko

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
            missingFiles.append(filename)
    
def processData(inDate, inExtensions):
    
    for ext in inExtensions:
    
        try:
            filename = '/home/admin/tmp/GEOSFP.' + inDate + '.' + ext + '.025x03125.nc'
            if (os.path.isfile(filename)):
                print 'Processing ' + filename
                processedFilename = '/home/admin/tmp/GEOSFP.' + inDate + '.' + ext + '.025x03125' + '.AU.nc'
                if (not os.path.isfile(processedFilename)):
                    pass
                    commandline = 'ncks -a -d lat,-46.0,-6.0 -d lon,110.0,155.0 ' + filename + ' ' + processedFilename
                    os.system(commandline)
                else:
                    print 'No need to process ' + processedFilename + ' as it already exists.'
            else:
                print filename + ' does not exist'
        except:
            print 'Error processing ' + filename
            corruptFiles.append(filename)
            
# Start of program
startDate = sys.argv[1]
extensions = ['A1', 'A3cld', 'A3dyn', 'A3mstC' , 'A3mstE', 'I3']
maxNumThreads = 11

year = startDate[:4]
month = startDate[4:6]

daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
if (int(year) % 4 == 0):
    daysInMonths[1] = 29

start = dt.datetime.now()
print start

missingFiles = []
corruptFiles = [] 

# Process only specified day
if (len(startDate) == 8):
        
    getData_html(startDate, extensions)
    processData(startDate, extensions)
    commandline =  'scp *' + startDate + '*.AU* gck574@raijin.nci.org.au:/g/data3/m19/geos-chem/data/GEOS_0.25x0.3125_AU/GEOS_FP/' 
    commandline = commandline + year + '/' + month + '/'
    os.system(commandline) 

# Process an entire month
else :
       
    # Get the number of days in the month to be processed
    daysInMonth = daysInMonths[int(month) - 1]
    numIters = int(daysInMonth / maxNumThreads)
    if (daysInMonth % maxNumThreads > 0):
        numIters += 1
    
    # Calculate the number of files that should be produced
    totalNumFiles = daysInMonth * 6
    
    startDay = 0
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
        
    # Check if all the files were copied to NCI
    
    # Set up the SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect to the host
    # Set up the SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('raijin.nci.org.au', username='gck574', key_filename = '/home/admin/.ssh/id_rsa')
    
    stdin, stdout, stderr = client.exec_command('ls /g/data3/m19/geos-chem/data/GEOS_0.25x0.3125_AU/GEOS_FP/' + year + '/' + month + ' | wc -l')
    
    ls_ret = []
    for line in stdout:
        ls_ret.append(line.strip('\n'))
    
    numCopiedFiles = int(ls_ret[0])
    if (numCopiedFiles == totalNumFiles):
        print 'Copied all files correctly'
    else:
        print 'Only ' + str(numCopiedFiles) + ' were copied. There should be ' + str(totalNumFiles) + ' for this month.'
        print 'Missing files:'
        for line in missingFiles:
            print line
        print 'Corrupt files:'
        for line in corruptFiles:
            print line
        
