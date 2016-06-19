#!/usr/bin/python3

import sys
import subprocess
import argparse
import platform

pyv=platform.python_version_tuple()

if pyv[0]!='3':
	print('Need python 3 for execute this script')
	sys.exit(1)

parser = argparse.ArgumentParser(description='Script for create a new mariadb server.')

parser.add_argument('--password', help='The password of the new server', required=True)

args = parser.parse_args()

#Dash, the default debian jessie shell, don't support <<<

print('Setting the password...')

if subprocess.call("echo 'mariadb-server mariadb-server/root_password password "+args.password+"' | sudo debconf-set-selections",  shell=True) > 0:
	print('Error, cannot set the password')
	sys.exit(1)
	
if subprocess.call("echo 'mariadb-server mariadb-server/root_password_again password "+args.password+"' | sudo debconf-set-selections",  shell=True) > 0:
	print('Error, cannot set the password again')
	sys.exit(1)
    
print('Setted the password')

#sudo debconf-set-selections <<< 'mariadb-server mariadb-server/root_password password your_password'
#sudo debconf-set-selections <<< 'mariadb-server mariadb-server/root_password_again password your_password'

if subprocess.call("sudo DEBIAN_FRONTEND=noninteractive apt-get -y install mariadb-server",  shell=True) > 0:
	print('Error')
	sys.exit(1)
else:
	print('Mariadb installed successfully')
	sys.exit(0)

