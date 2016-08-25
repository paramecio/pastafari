#!/usr/bin/env python3

import subprocess
import re

if subprocess.call("sudo apt-get install -y quota",  shell=True) > 0:
    print('Error')
    sys.exit(1)

out=subprocess.getoutput('df /home')

arr_out=out.split("\n")

info_df=arr_out[1].split(" ")

disk=info_df[-1]

arr_line=[]

pattern_quota=re.compile('.*usrquota,grpquota.*')

pattern_disk=re.compile('.*\s'+disk.replace('/', '\/')+'\s.*')

#UUID=fd7bf62a-3dc3-439e-a975-dcb7d03bc686 /               ext4    errors=remount-ro 0       1

print("Updating fstab...")

line_fstab=re.compile(r"(.*?)(\s+)(.*?)(\s+)(.*?)(\s+)(.*?)(\s+)(.*?)(\s+)(.*?)")

no_quota=0

with open('/etc/fstab') as f:
    for line in f:

        first=line[:1]
        if first!="#" and first!="\n":
            if pattern_disk.match(line) and not pattern_quota.match(line):
                line=line_fstab.sub(r"\1\2\3\4\5\6\7,usrquota,grpquota\8\9\10\11", line)
                no_quota=1

            #print(line.strip())
        arr_line.append(line.strip())
        
if no_quota==1:

    final_fstab="\n".join(arr_line)

    with open('/etc/fstab', 'w') as f:

        f.write(final_fstab)

    print("Remounting %s with quota support" % disk)

    if subprocess.call("sudo mount -o remount %s" % disk,  shell=True) > 0:
        print('Error: cannot remount the filesystem with quota!')
        sys.exit(1)

    print("Creating quota files...")

    if subprocess.call("sudo quotacheck -cugm %s" % disk,  shell=True) > 0:
        print('Error: cannot create the quota files!')
        sys.exit(1)
        
    print("Enabling quota...")

    if subprocess.call("sudo quotaon %s" % disk,  shell=True) > 0:
        print('Error: cannot enable quota!')
        sys.exit(1)

print("Finished quota configuration...")
