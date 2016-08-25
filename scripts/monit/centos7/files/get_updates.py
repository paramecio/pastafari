#!/usr/bin/python3.5

import subprocess
import re
import urllib.request
import urllib.parse

pattern=re.compile('^Inst (.*?)$')

"""
if subprocess.call('sudo yum -y update',  shell=True) > 0:
    print('Error, cannot update yum')
    exit(1)
else:
    print('Your apt-get database is updated, checking if you have updates...')
"""

with subprocess.Popen(["val_update=$(yum check-update) && echo $val_update | egrep \"(.i386|.x86_64|.noarch|.src)\" | wc -l"], shell=True, stdout=subprocess.PIPE) as proc:
    
    num_updates=proc.stdout.read().decode("utf-8")

url="http://url/to/server/token/ip"

data = urllib.parse.urlencode({'num_updates': int(num_updates)})

data = data.encode('ascii')

content=urllib.request.urlopen(url, data)
