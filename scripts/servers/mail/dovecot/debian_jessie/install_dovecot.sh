#!/bin/bash

sudo apt-get install -y dovecot-common dovecot-imapd dovecot-pop3d

if [ $? -eq 0 ]; then
    echo "Installed Dovecot successfully"
else
    echo "Error installing Dovecot..."
    exit 1;
fi

sudo cp modules/pastafari/scripts/servers/mail/dovecot/debian_jessie/files/10-auth.conf /etc/dovecot/conf.d/
sudo cp modules/pastafari/scripts/servers/mail/dovecot/debian_jessie/files/10-mail.conf /etc/dovecot/conf.d/
sudo cp modules/pastafari/scripts/servers/mail/dovecot/debian_jessie/files/10-master.conf /etc/dovecot/conf.d/
sudo cp modules/pastafari/scripts/servers/mail/dovecot/debian_jessie/files/10-ssl.conf /etc/dovecot/conf.d/

sudo systemctl restart dovecot

echo "Finished dovecot configuration"
