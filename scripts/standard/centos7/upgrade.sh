#!/bin/sh

echo "Upgrading system..."

sudo yum -y upgrade

echo "Upgraded if not error..."

echo "Checking for new updates..."

sudo /etc/cron.daily/get_updates.py

