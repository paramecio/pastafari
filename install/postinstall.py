#!/usr/bin/python3

import shutil
import os
import argparse
from paramecio.citoplasma.keyutils import create_key
from subprocess import call

src='modules/pastafari/install/files/config_admin.py'
dst='settings/config_admin.py'

src_launcher='modules/pastafari/install/files/launcher.py'
dst_launcher='launcher.py'

src_scheduler='modules/pastafari/install/files/scheduler.py'
dst_scheduler='scheduler.py'

if not shutil.copy(src, dst):
    print('Error: cannot copy the admin configuration')
    
if not shutil.copy(src_launcher, dst_launcher):
    print('Error: cannot copy the launcher')
    
if not shutil.copy(src_scheduler, dst_scheduler):
    print('Error: cannot copy the scheduler')

#Install paramiko

if call("pip3 install paramiko"), shell=True) > 0:
    print('Error, cannot  install Paramiko')
    exit(1)
else:
    print('Added paramiko')

# Generating rsa key

import paramiko

rsa_key=paramiko.RSAKey.generate(2048)

password=create_key(20)

try:
    os.mkdir('ssh/')
except:
    print('Error, cannot  install ssh keyfiles')
    exit(1)

private_key_file='ssh/id_rsa'
pub_key_file='ssh/id_rsa.pub'

rsa_key.write_private_key_file(filename, password)

with open(pub_key_file, 'w') as f:
    f.write(rsa_key.get_base64())
    
print('Generated rsa key...')

# Open the config and write this data

api_key=create_key(50)

"""
config_task.public_key='ssh/id_rsa.pub'
	
config_task.private_key='/home/absurdo/.ssh/id_rsa'

config_task.password_key='747mxcom'

config_task.deny_missing_host_key=False

config_task.api_key="key"

config_task.url_monit='http://192.168.1.79:8080/monit/getinfo'
"""
