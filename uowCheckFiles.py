#!/usr/bin/env python

import paramiko

# Set up the SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the host
# Set up the SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('raijin.nci.org.au', username='gck574', key_filename = 'c:/Users/grahamk/.ssh/id_rsa')

stdin, stdout, stderr = client.exec_command('cd tmp')
stdin, stdout, stderr = client.exec_command('ls /g/data3/m19/geos-chem/data/GEOS_0.25x0.3125_AU/GEOS_FP/2018/02 | wc -l')

ls_ret = []
for line in stdout:
    ls_ret.append(line.strip('\n'))
    
