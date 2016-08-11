#!/bin/bash

sudo apt-get install -y sqlgrey

if [ $? -eq 0 ]; then
    echo "Installed SQLGrey successfully"
else
    echo "Error installing sqlgrey..."
    exit 1;
fi

sudo apt-get install libdbd-sqlite3-perl

if [ $? -eq 0 ]; then
    echo "Installed sqlite-perl sucesffully"
else
    echo "Error installing sqlite-perl..."
    exit 1;
fi

sudo chown sqlgrey:sqlgrey /var/lib/sqlgrey

sudo cp modules/pastafari/scripts/servers/mail/sqlgrey/debian_jessie/files/sqlgrey.conf /etc/sqlgrey/

sudo systemctl restart sqlgrey

echo "Finished sqlgrey install..."
