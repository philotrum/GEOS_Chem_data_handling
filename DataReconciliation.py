import paramiko
import base64

# Recursive function to drill down into directory structures
def drill(inDir, inStructure):

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
    stdin, stdout, stderr = client.exec_command(command + inDir)
    
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
            drill(recursiveDir, inStructure)
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

#*****************************
# Start of program execution
#*****************************

# Path to all input files
basePath = 'c:\users\grahamk\documents\docs\jenny fisher\\'

# Select the server you want to interrogate by commenting/uncommenting
hostServer = 'HPC'
#hostServer = 'NCI'

# Set up login information
if hostServer == 'NCI':
    passwordFilename = 'loginNCI.txt'
    loginName = 'gck574'
    serverAddress = 'raijin.nci.org.au'
else:
    passwordFilename = 'loginHPC.txt'
    loginName = 'grahamk'
    serverAddress = 'hpc.its.uow.edu.au'

# Read in encrypted password. The encryoted password is stored
# in a file, and has been encrypted by running
# the password through base64.b64encode. I did it
# in a runtime window. I can write a small program
# to allow users to encode their password and store it
# in a file.
# This is just so that I can share the script without
# risking accidentally sharing my password. The password
# file would be kept in the user's home directory. The file
# should only be readable by the user, not others or group.
with open(basePath + passwordFilename) as ins:
    encoded = ins.readline()
        
# Decode the password
myPassword = base64.b64decode(encoded)

# Set up the SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the host
client.connect(serverAddress, username=loginName, password=myPassword)

# Clear the decrypted password
myPassword = ''

# Create a list to store the results of the interrogation.
# This is a list to which I add more and more lists.
# At each level I store the name and depth of the directory I am in,
# a list of directories and a list of the files in the directory.
# I can add other lists of any other information we might need
# that is returned by the ls -l command. This is just proof of concept.
structure = []

# Initialise a couple of attribute variables for the recursive function.
# Python allows you to effectively create static variables that are associated
# with a function.

# drill.depth allows me to track how deep into the file structure I am
drill.depth = 0
# drill.hostserver allows me to run different commands depending on the machine
# I am inspecting. NCI uses a limited set of commands and prefixes them with
# mdss to manage the tape storage system.
drill.server = hostServer

# Call the recursive function passing it the base directory being
# interrogated.
if (hostServer == 'NCI'):
    drill('./geos-chem', structure)
else:
    drill('/hpc/data/chemistry/CAC/GEOS_Chem', structure)

# Close the SSH client
client.close()