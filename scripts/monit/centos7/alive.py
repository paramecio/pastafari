#!/usr/bin/python3.5 -u

# A script for install alive script 

import subprocess
import argparse
import re
import os
import shutil
from subprocess import call

parser = argparse.ArgumentParser(description='A script for install alive script and cron')

parser.add_argument('--url', help='The url where notify that this server is alive', required=True)
parser.add_argument('--user', help='The user for pastafari', required=True)
parser.add_argument('--pub_key', help='The pub key used in pastafari user', required=True)

args = parser.parse_args()

url=args.url

check_url = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if check_url.match(args.url):
    
    # Create users
    
    if call("sudo useradd -m -s /bin/sh %s" % args.user, shell=True) > 0:
        print('Error, cannot add a new user')
        exit(1)
    else:
        print('Added user')
        
    if call("sudo mkdir -p /home/"+args.user+"/.ssh && sudo chown "+args.user+":"+args.user+" /home/"+args.user+"/.ssh && sudo chmod 700 /home/"+args.user+"/.ssh", shell=True) > 0:
        print('Error, cannot add ssh directory')
        exit(1)
    else:
        print('Added ssh directory')
        
    if call("sudo cp "+args.pub_key+" /home/"+args.user+"/.ssh/authorized_keys && sudo chown "+args.user+":"+args.user+" /home/"+args.user+"/.ssh/authorized_keys && sudo chmod 600 /home/"+args.user+"/.ssh/authorized_keys", shell=True) > 0:
        print('Error, cannot pub key to user')
        exit(1)
    else:
        print('Added pub key to user')
    
    # Edit alive cron 
    
    with open('modules/pastafari/scripts/monit/centos7/files/crontab/alive') as f:
        alive_cron=f.read()
    
    with open('modules/pastafari/scripts/monit/centos7/files/crontab/alive', 'w') as f:
        alive_cron=alive_cron.replace('/home/spanel/modules/pastafari/scripts/monit/centos7/files/get_info.py', '/usr/local/bin/get_info.py')
        f.write(alive_cron)
    
    # Edit get_info.py
    
    with open('modules/pastafari/scripts/monit/centos7/files/get_info.py') as f:
        get_info=f.read()

    with open('/usr/local/bin/get_info.py', 'w') as f:
        get_info=get_info.replace("http://url/to/server/token/ip", args.url)
        f.write(get_info)
        
    os.chmod('/usr/local/bin/get_info.py', 0o700)
    shutil.chown('/usr/local/bin/get_info.py', args.user, args.user)
    
    # Edit get_updates.py
    
    with open('modules/pastafari/scripts/monit/centos7/files/get_updates.py') as f:
        get_updates=f.read()

    with open('/etc/cron.daily/get_updates.py', 'w') as f:
        url_updates=args.url.replace('/getinfo/', '/getupdates/')
        get_updates=get_updates.replace("http://url/to/server/token/ip", url_updates)
        f.write(get_updates)
    
    os.chmod('/etc/cron.daily/get_updates.py', 0o700)
    
    # Edit sudo file

    with open('modules/pastafari/scripts/monit/centos7/files/sudoers.d/spanel') as f:
        sudoers=f.read()

    with open('/etc/sudoers.d/spanel', 'w') as f:
        sudoers=sudoers.replace("spanel", args.user)
        f.write(sudoers)
    
    # Copy cron alive to /etc/cron.d/
    
    if call("sudo cp modules/pastafari/scripts/monit/centos7/files/crontab/alive /etc/cron.d/alive", shell=True) > 0:
        print('Error, cannot install crontab alive file in cron.d')
        exit(1)
    else:
        print('Added contrab alive file in cron.d')
    
    print('Script installed successfully')
    
    # Copy script for upgrades in /usr/local/bin
    
    if call("mkdir /home/"+args.user+"/bin/ && cp modules/pastafari/scripts/standard/centos7/upgrade.sh /home/"+args.user+"/bin/ && chown -R "+args.user+":"+args.user+" /home/"+args.user+"/bin/", shell=True) > 0:
        print('Error, cannot install upgrade.py in /home/'+args.user+'/bin/')
        exit(1)
    else:
        print('Added /home/'+args.user+'/bin/upgrade.py')
    
    print('Script installed successfully')
    
    # Making first call to site

    if subprocess.call('/usr/local/bin/get_info.py',  shell=True) > 0:
        print('Error')
        exit(1)
    else:
        print('Your server should be up in your panel...')
    
    exit(0)
    
else:
    
    print('Error installing the module, not valid url')
    
    exit(1)
    
