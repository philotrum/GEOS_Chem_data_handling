import threading, os
import datetime as dt

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
        
startTime = dt.datetime.now()

extensions = ['A1', 'A3cld', 'A3dyn', 'A3mstC' , 'A3mstE', 'I3']

year = '2018'
month = '09'

missingFiles = []
corruptFiles = [] 


daysInMonth = 11
threads = []
day = 1
for i in range(daysInMonth):

    date = year + month + str(day).zfill(2)
    t = threading.Thread(target = processData, args = (date,))
    threads.append(t)
    day += 1

for x in threads:
    x.start()

for x in threads:
    x.join()

totalTime = dt.datetime.now() - startTime
print('Total time: ' + str(totalTime))