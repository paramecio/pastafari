#!/bin/bash

sudo apt-get install -y opendkim opendkim-tools

if [ $? -eq 0 ]; then
    echo "Installed OpenDkim successfully"
else
    echo "Error installing OpenDKIM..."
    exit 1;
fi

sudo mkdir -p /etc/opendkim

sudo touch /etc/opendkim/KeyTable
sudo touch /etc/opendkim/SigningTable

sudo chgrp opendkim /etc/opendkim/ *
sudo chmod g+r /etc/opendkim/ * 

sudo cp modules/pastafari/scripts/servers/mail/opendkim/debian_jessie/files/opendkim.conf /etc/opendkim.conf
sudo cp modules/pastafari/scripts/servers/mail/opendkim/debian_jessie/files/opendkim /etc/default/

sudo systemctl restart opendkim

echo "Finished opendkim configuration"
