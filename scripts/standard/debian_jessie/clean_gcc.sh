#!/bin/bash

sudo apt-get remove -y --auto-remove build-essential gcc 

if [ $? -eq 0 ]; then
    echo "Cleaned gcc sucessfully"
else
    echo "Error dropping gcc..."
    exit;
fi
