#!/usr/bin/python3

import subprocess

if subprocess.call("sudo apt-get install -y quota",  shell=True) > 0:
        print('Error')
        sys.exit(1)

out=subprocess.getoutput('df /home')

arr_out=out.split("\n")

info_df=arr_out[1].split(" ")

disk=info_df[-1]

arr_line=[]

with open('/etc/fstab') as f:
    for line in f:
        arr_line.append(line)
        first=line[:1]
        if first!="#" and first!="\n":
            print(line.strip())

