#!/bin/sh

echo "Updating apt-get..."

sudo DEBIAN_FRONTEND="noninteractive" apt-get -y update

echo "Installing python3"

sudo DEBIAN_FRONTEND="noninteractive" apt-get install -y python3

echo "Installed python3 sucessfully if not error..."

