#!/usr/bin/python3

import shutil
import os
import sys

working_directory=os.getcwd()

sys.path.insert(0, working_directory)

import argparse
from paramecio.citoplasma.keyutils import create_key
from settings import config
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

if call("pip3 install paramiko", shell=True) > 0:
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

rsa_key.write_private_key_file(private_key_file, password)

with open(pub_key_file, 'w') as f:
    f.write(rsa_key.get_base64())
    
print('Generated rsa key...')

# Open the config and write this data

api_key=create_key(50)

add_config=[]

add_config.append("\n\nfrom modules.pastafari.libraries.configclass import config_task")
add_config.append("from paramecio.citoplasma.sendmail import SendMail")

add_config.append("# Pastafari configuration")

add_config.append("config_task.public_key='%s'" %  pub_key_file)
	
add_config.append("config_task.private_key='%s'" % private_key_file)

add_config.append("config_task.password_key='%s'" % password)

add_config.append("config_task.deny_missing_host_key=False")

add_config.append("config_task.api_key='%s'" % api_key)

add_config.append("config_task.url_monit='%s/monit/getinfo'" % config.domain_url)

# Add this elements in config.py

with open('settings/config.py', 'a') as f:
    f.write("\n\n".join(add_config))

print('Writed config...')

#Install cron

#cron_dir=input('The directory where cron notification script is installed (by default /etc/cron.d): ').strip()

with open('modules/pastafari/install/files/crontab') as f:
    cron_file=f.read()
    
cron_file=cron_file.replace('/path/to/pastafari', working_directory)

with open('modules/pastafari/install/files/crontab', 'w') as f:
    f.write(cron_file)

if call("crontab modules/pastafari/install/files/crontab", shell=True) > 0:
    print('Error, cannot  install the cron file')
    exit(1)
else:
    print('Added cron file')
    
#Configure mail

"""
SendMail.port=587
    
SendMail.host='web-t-sys.com'
    
SendMail.username='absurdo'
    
SendMail.password='irpfxion'

SendMail.ssl=False

email_address='webmaster@web-t-sys.com'

email_notification='webmaster@web-t-sys.com'
"""

host_email=input('Server host: ').strip()

if host_email=='':
    print('Error, you need a mail server')
    exit(1)

port_email=input('SMTP port (default port 25): ').strip()

user_email=input('Email username: ').strip()

if user_email=='':
    print('Error, you need a mail username')
    exit(1)
    
pass_email=input('Email password: ').strip()

if pass_email=='':
    print('Error, you need a mail password')
    exit(1)
    
ssl_email=input('Email use ssl? (default: yes): ').strip().lower()

if ssl_email=='' or ssl_email=='yes':
    ssl_email=True
elif ssl_email=='no':
    ssl_email=False
else:
    ssl_email=True
    
if port_email=='':
    port_email=25
else:
    try:
        port_email=int(port_email)
    except:
        port_email=25

email_address=input('The email address that define the email from: ').strip().lower()
        
if email_address=='':
    print('Error, you need a mail name')
    exit(1)
    
email_notification=input('The email address where notification are sended: ').strip().lower()
        
if email_notification=='':
    print('Error, you need a mail name for send notification')
    exit(1)



print('Finished pastafari install')
