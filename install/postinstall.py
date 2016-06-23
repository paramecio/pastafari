#!/usr/bin/python3

import shutil

src='modules/pastafari/install/files/config_admin.py'
dst='settings/config_admin.py'

if not shutil.copy(src, dst):
    print('Error: cannot copy the admin configuration')

