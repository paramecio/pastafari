#!/bin/bash

sudo apt-get install -y sqlite

if [ $? -eq 0 ]; then
    echo "Installed sqlite successfully"
else
    echo "Error installing sqlite..."
    exit;
fi
