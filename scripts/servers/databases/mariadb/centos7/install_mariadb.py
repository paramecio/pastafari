#!/usr/bin/python3.5

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

#sudo debconf-set-selections <<< 'mariadb-server mariadb-server/root_password password your_password'
#sudo debconf-set-selections <<< 'mariadb-server mariadb-server/root_password_again password your_password'

# Delete mariadb standard packages if exists

if subprocess.call("sudo yum -y remove mariadb-server mariadb-libs",  shell=True) > 0:
	print('Error,cannot remove olds mariadb versions')
	sys.exit(1)

print('Installing MariaDB from uis repos...')

if subprocess.call("sudo yum -y install mariadb100u-server",  shell=True) > 0:
	print('Error')
	sys.exit(1)

print('Setting the password and securing the installation...')

#if subprocess.call("sudo mysqladmin -u root password "+args.password,  shell=True) > 0:
if subprocess.call("sudo myql --user=root <<_EOF_ \
UPDATE mysql.user SET Password=PASSWORD('"+args.password+" WHERE User='root';\
DELETE FROM mysql.user WHERE User=''; \
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1'); \
DROP DATABASE IF EXISTS test; \
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'; \
FLUSH PRIVILEGES; \
_EOF_",  shell=True) > 0:
	print('Error, cannot set the password')
	sys.exit(1)
else:
	print('Mariadb installed successfully')
	sys.exit(0)
    
"""	
if subprocess.call("sudo echo 'mariadb-server mariadb-server/root_password_again password "+args.password+"' | sudo debconf-set-selections",  shell=True) > 0:
	print('Error, cannot set the password again')
	sys.exit(1)
"""
    
print('Setted the password')
