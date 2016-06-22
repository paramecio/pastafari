#!/usr/bin/python3

import psutil
import json
import urllib.request
import urllib.parse

#url="http://url/to/info"

url="http://url/to/server/token/ip"

network_info=psutil.net_io_counters(pernic=False)

network_devices=psutil.net_if_addrs()

cpu_idle=psutil.cpu_percent(interval=1)

disk_info=psutil.disk_partitions()

partitions={}

for disk in disk_info:
    
    partition=str(disk[1])
    partitions[partition]=psutil.disk_usage(partition)
    #print(partition+"="+str(partitions[partition]))

dev_info={}

mem_info=psutil.virtual_memory()

#for device, info in network_info.items():
    
    #{'eth0': netio(bytes_sent=485291293, bytes_recv=6004858642, packets_sent=3251564, packets_recv=4787798, errin=0, errout=0, dropin=0, dropout=0),
    
    #dev_info[device]=[info[0], info[1]]


#for device, info in network_devices.items():
    
    #print(info)
json_info=json.dumps({'net_info': network_info, 'cpu_idle': cpu_idle, 'disks_info': partitions, 'mem_info': mem_info})

data = urllib.parse.urlencode({'data_json': json_info})

data = data.encode('ascii')

content=urllib.request.urlopen(url, data)



