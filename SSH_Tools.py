import paramiko

# Recursive function to drill down into directory structures
def drill(inDir, inStructure, inSSHClient):

    # Increment the depth counter
    drill.depth += 1
    
    # Create a temporary list to store the information about this directory
    tmpRow = []
    # Append the directory name and depth
    tmpRow.append(inDir)
    tmpRow.append(drill.depth)
    
    # Create lists to store the listing of directories and files in this
    # directory
    dirs = []
    files = []
    
    # give the user some feedback so that they know that something
    # is happenning
    print 'drill ' + inDir
    
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
    
    # split the returned lines into a list
    ret_split = []
    for row in ls_ret:
        ret_split.append(row.split(' '))
    
    # Store the returned information on the directories and files
    # in this directory in the appropriate lists.    
    for row in ret_split[1:]:
        nextListingName = row[len(row) -1]
        # If the next listing is a directory...
        if (row[0].find('d') != -1):
            # Append the directory name to the directories list
            dirs.append(nextListingName)
            # Make the recursive call
            recursiveDir = inDir + '/' + nextListingName
            drill(recursiveDir, inStructure, inSSHClient)
        # Otherwise it is a file, so appand it to the files list
        else:
            files.append(nextListingName)
            
    # Add the lists to the temporary list
    tmpRow.append(dirs)
    tmpRow.append(files)
    # Append the information to the structure that holds all the
    # data.
    inStructure.append(tmpRow)
    
    # Decrement the depth counter before leavin the fucntion
    drill.depth -= 1
