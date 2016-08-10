#!/bin/bash

sudo apt-get install -y opendkim opendkim-tools

if [ $? -eq 0 ]; then
    echo "Installed OpenDkim successfully"
else
    echo "Error installing OpenDKIM..."
    exit;
fi

sudo chown sqlgrey:sqlgrey /var/lib/sqlgrey

sudo cp modules/pastafari/scripts/servers/mail/sqlgrey/debian_jessie/files/sqlgrey.conf /etc/sqlgrey/
