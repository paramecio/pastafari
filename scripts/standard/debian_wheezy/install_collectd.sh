#!/bin/sh

sleep 2

sudo DEBIAN_FRONTEND="noninteractive" apt-get install -y collectd

echo "Installed collectd sucessfully if not error..."

