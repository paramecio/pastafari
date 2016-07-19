#!/bin/sh

echo "Updating apt-get..."

sudo DEBIAN_FRONTEND="noninteractive" apt-get -y update

echo "Upgrading system..."

sudo DEBIAN_FRONTEND="noninteractive" apt-get -y upgrade

echo "Upgraded if not error..."

echo "Checking for new updates..."

sudo /etc/cron.daily/get_updates.py

