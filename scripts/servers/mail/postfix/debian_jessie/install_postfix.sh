#!/bin/bash

sudo debconf-set-selections <<< "postfix postfix/mailname string `hostname -f`"
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
sudo apt-get install -y postfix

if [ $? -eq 0 ]; then
    echo "Installed successfully"
else
    echo "Error installing postfix..."
    exit;
fi

sudo apt-get install -y maildrop

if [ $? -eq 0 ]; then
    echo "Installed Maildrop successfully"
else
    echo "Error installing Maildrop..."
    exit;
fi

sudo cp modules/pastafari/scripts/servers/mail/postfix/debian_jessie/files/main.cf /etc/postfix/

if [ $? -eq 0 ]; then
    echo "Installed sucessfully main.cf"
else
    echo "Error installing postfix configuration..."
    exit;
fi

HOSTNAME_SERVER=`hostname -f`

sudo sed -i -e 's/alfa\.example\.com/'$HOSTNAME_SERVER'/g' /etc/postfix/main.cf

sudo /etc/postfix/transport < "autoreply.$HOSTNAME_SERVER  autoreply:"

sudo postmap hash:/etc/postfix/transport

sudo touch /etc/postfix/virtual_mailbox
sudo touch /etc/postfix/virtual_domains

sudo postmap hash:/etc/postfix/virtual_mailbox
sudo postmap hash:/etc/postfix/virtual_domains

sudo postfix reload

if [ $? -eq 0 ]; then
    echo "Reloaded postfix sucessfully"
else
    echo "Error reloading postfix..."
    exit;
fi
