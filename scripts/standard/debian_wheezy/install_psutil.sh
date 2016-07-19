#!/bin/sh

# Install pip

sudo DEBIAN_FRONTEND="noninteractive" apt-get install -y python3-pip

sudo pip-3.2 install psutil

echo "Installed python3-psutil sucessfully if not error..."

