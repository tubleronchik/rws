#!/bin/bash
DEVICE_ID=""
if [ ! -d "./rws" ] 
then 
    git clone https://github.com/tubleronchik/rws
fi
cd rws/docker
sudo DEVICE_ID="$DEVICE_ID" docker-compose up
