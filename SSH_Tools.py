
class fields:
    dirName = 0
    dirList = 1
    fileList = 2
    fileSize = 4

# Recursive function to drill down into directory structures
def drill(inDir, inSSHClient):
   
    # Append the directory name
    # Trim off the path
    dirInfo = []    
    dirInfo.append(inDir)
    
    # Create lists to store the listing of directories and files in this
    # directory
    dirs = []
    files = []
     
    # give the user some feedback so that they know that something
    # is happenning
    print 'drill ' + inDir
    
    # Get the ls - l information. It comes back as an array
    ret = get_ls_array(inDir, inSSHClient)
        
    # Store the returned information on the directories and files
    # in this directory in the appropriate lists.    
    for row in ret[1:]:
        nextListingName = row[len(row) -1]
        # If the next listing is a directory...
        if (row[0].find('d') != -1):
            recursiveDir = inDir + '/' + nextListingName
            dirs.append(drill(recursiveDir, inSSHClient))
        # Otherwise it is a file, so append it to the files list
        else:
            tmp = []
            tmp.append(nextListingName)
            tmp.append(int(row[fields.fileSize]))
            files.append(tmp)
            
    # Add the lists to the stucture
    dirInfo.append(dirs)
    dirInfo.append(files)
    
    # Append the information on this directory to the stucture
    return dirInfo
    
def get_ls_array(inDir, inSSHClient):
    
    # Set the command depending on the machine we are on
    if (drill.server == 'NCI'):
        command = 'mdss ls -l '
    else:
        command = 'ls -l '
        
    # Run the command and set up the return streams
    stdin, stdout, stderr = inSSHClient.exec_command(command + inDir)
    
    # Read in the returned information stripping off the newline
    ls_ret = []
    for line in stdout:
        ls_ret.append(line.strip('\n'))
    
    # Reduce all multiple spaces to 1 space so that I can
    # split the string reliably.
    index = 1
    for line in ls_ret[1:]:
        while (line.find('  ') != -1):
            line = line.replace('  ', ' ')
        ls_ret[index] = line
        index += 1
        
    # split the returned lines into a list
    ret_split = []
    for row in ls_ret:
        ret_split.append(row.split(' '))
        
    return ret_split
    
def print_File_Structure(inStructure, inOutS):
    
    print_Dir_List.depth = -1
    print_Dir_List(inStructure, inOutS)

# Recursive print function
def print_Dir_List(inList, inOutS):
    
    print_Dir_List.depth += 1
    
    for currDir in inList[fields.dirList]:
        padding = ''
        for i in range(print_Dir_List.depth):
            padding += '-'

        dirName = currDir[fields.dirName]
        trimmedDirName = dirName[dirName.rfind('/') + 1:]
        inOutS.write(padding + trimmedDirName + '\n')
        
        # Recursive call...
        print_Dir_List(currDir, inOutS)
        
        for file in currDir[fields.fileList]:
             inOutS.write(padding + '-' + str(file[0]) +' ' + str(file[1]) + '\n')
        
    print_Dir_List.depth -= 1