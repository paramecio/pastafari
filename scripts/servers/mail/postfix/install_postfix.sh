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

sudo apt-get install -y procmail

if [ $? -eq 0 ]; then
    echo "Installed Procmail successfully"
else
    echo "Error installing procmail..."
    exit;
fi

sudo cp modules/pastafari/scripts/servers/mail/postfix/debian_jessie/files/main.cf /etc/postfix/

if [ $? -eq 0 ]; then
    echo "Installed sucessfully main.cf"
else
    echo "Error installing postfix configuration..."
    exit;
fi

sudo HOSTNAME_SERVER=`hostname -f` sed -i -e 's/alfa.example.com/'$HOSTNAME_SERVER'/g' /etc/postfix/main.cf

sudo postfix reload

if [ $? -eq 0 ]; then
    echo "Reloaded postfix sucessfully"
else
    echo "Error reloading postfix..."
    exit;
fi
