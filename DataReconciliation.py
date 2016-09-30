import paramiko
import base64
#import io
#Dataimport sys

from SSH_Tools import *

#*****************************
# Start of program execution
#*****************************

# Path to all input files
basePath = 'c:\users\grahamk\documents\docs\jenny fisher\\'

# Select the server you want to interrogate by commenting/uncommenting
hostServer = 'HPC'
#hostServer = 'NCI'

# Set up login information.
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

# Initialise a couple of attribute variables for the recursive function.
# Python allows you to effectively create static variables that are associated
# with a function.

# drill.hostserver allows me to run different commands depending on the machine
# I am inspecting. NCI uses a limited set of commands and prefixes them with
# mdss to manage the tape storage system.
drill.server = hostServer

# Set up the empty list to store the filesystem structure in.
structure = []

# Call the recursive function passing it the base directory being
# interrogated.
if (hostServer == 'NCI'):
    structure = drill('./geos-chem', client)
else:
    #structure = drill('/hpc/data/chemistry/CAC/GEOS_Chem/GEOS_2x2.5', client)
    structure = drill('./drillTest', client)

# Close the SSH client
client.close()

outS = open('output.txt', mode = 'w')

print_File_Structure(structure, outS)

#structure = []

outS.close()