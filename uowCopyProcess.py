#!/usr/bin/env python3.5

# This file copies global GEOSChem input files from the ComputeCanada server, extracts the data for 
# the Australian region into another file, and then copies the files to NCI for use.

# Usage:
#   python uowCopyProcess yyyymmdd    - copies and processes the data for the specified day
#   python uowCopyProcess yyyymm      - copies and processes all data for the entire month specified.

import sys, os
from ftplib import FTP
import wget
import threading
from multiprocessing import Pool
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
                print(filename + ' already exists. No need to copy.')
        except:
            print(filename + ' failed to copy from the remote server.')
    
    ftp.quit()
    ftp = None
    
def getData_html(inDate):
    
    url = 'http://geoschemdata.computecanada.ca/GEOS_0.25x0.3125/GEOS_FP/' + year + '/' + month + '/'
    
    for ext in extensions:
        
        try:
            filename = 'GEOSFP.' + inDate + '.' + ext + '.025x03125.nc'
            remoteFilename = url + filename
            print('Remote filename: ' + remoteFilename)
            if (not os.path.isfile(filename)):
                #urllib.urlretrieve(remoteFilename, filename)
                wget.download(remoteFilename, filename)
            else:
                print(filename + ' already exists. No need to copy.')
        except:
            print(filename + ' failed to copy from the remote server.')
            missingFiles.append(filename)
    
def processData(inDate):
    
    for ext in extensions:    
        try:
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
        except:
            print('Error processing ' + filename)
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

startTime = dt.datetime.now()
print('Start time: ' + str(startTime))

missingFiles = []
corruptFiles = [] 

# Process only specified day
if (len(startDate) == 8):
        
    getData_html(startDate)
    processData(startDate)
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
            print(date)
            t = threading.Thread(target = getData_html, args = (date,))
            threads.append(t)
        
        for x in threads:
            x.start()
            
        for x in threads:
            x.join()
    
    downloadFinish = dt.datetime.now()
    downloadTime = downloadFinish - startTime
    print('Download time: ' + str(downloadTime))
    
    threads = None

    daysToProcess = [year + month + str(day).zfill(2) for day in range(1, daysInMonth)]
    args = [daysToProcess]
    with Pool() as p:
        p.map(processData, daysToProcess)

    processFinish = dt.datetime.now()
    processTime = processFinish - downloadFinish
    print('Processing time: ' + str(processTime))

    for day in daysToProcess:
        
        commandline =  'scp *' + day + '*.AU* gck574@raijin.nci.org.au:/g/data3/m19/geos-chem/data/GEOS_0.25x0.3125_AU/GEOS_FP/' 
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
        print('Copied all files correctly')
    else:
        print('Only ' + str(numCopiedFiles) + ' were copied. There should be ' + str(totalNumFiles) + ' for this month.')
        print('Missing files:')
        for line in missingFiles:
            print(line)
        print('Corrupt files:')
        for line in corruptFiles:
            print(line)
        
    copyFinish = dt.datetime.now()
    copyTime = copyFinish - processFinish
    print('Copy time: ' + str(copyTime))
    totalTime = copyFinish - startTime
    print('Total time: ' + str(totalTime))