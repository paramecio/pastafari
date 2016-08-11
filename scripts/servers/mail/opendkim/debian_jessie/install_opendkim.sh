#!/bin/bash

sudo apt-get install -y opendkim opendkim-tools

if [ $? -eq 0 ]; then
    echo "Installed OpenDkim successfully"
else
    echo "Error installing OpenDKIM..."
    exit 1;
fi

sudo mkdir -p /etc/postfix/dkim/

sudo touch /etc/postfix/dkim/keytable
sudo touch /etc/postfix/dkim/signingtable 

sudo chgrp opendkim /etc/postfix/dkim/ *
sudo chmod g+r /etc/postfix/dkim/ * 

sudo cp modules/pastafari/scripts/servers/mail/opendkim/debian_jessie/files/opendkim.conf /etc/opendkim.conf
sudo cp modules/pastafari/scripts/servers/mail/opendkim/debian_jessie/files/opendkim /etc/default/

sudo systemctl restart opendkim

echo "Finished opendkim configuration"
