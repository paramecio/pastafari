#!/bin/bash

sudo apt-get install -y sqlgrey

if [ $? -eq 0 ]; then
    echo "Installed SQLGrey successfully"
else
    echo "Error installing sqlgrey..."
    exit;
fi

sudo chown sqlgrey:sqlgrey /var/lib/sqlgrey

sudo cp modules/pastafari/scripts/servers/mail/sqlgrey/debian_jessie/files/sqlgrey.conf /etc/sqlgrey/
