#!/bin/bash
echo "Configuring workspace. Please wait..."
if [ ! -d "./rws-main" ] 
then 
    echo "Downloading scripts..."
    sudo apt update
    sudo apt install python3-pip
    wget https://github.com/tubleronchik/rws/archive/main.zip > /dev/null 2>&1
    unzip main.zip > /dev/null 2>&1
    echo "Done"
    cd rws-main
    echo 'Installing dependencies...'
    pip3 install -r requirements.txt > /dev/null 2>&1 
    echo "Done"
else
    cd rws-main
fi
if [ ! -d "./go-ipfs" ]
then
    echo "Installing ipfs daemon. You will need to enter your passwword"
    wget https://dist.ipfs.io/go-ipfs/v0.8.0/go-ipfs_v0.8.0_linux-amd64.tar.gz > /dev/null 2>&1
    tar -xzf go-ipfs_v0.8.0_linux-amd64.tar.gz > /dev/null 2>&1 
    cd go-ipfs
    sudo bash install.sh > /dev/null 2>&1 
    ipfs init > /dev/null 2>&1
    echo "Done"
    cd ..
fi
ipfs daemon --enable-pubsub-experiment > /dev/null 2>&1 &
echo "Worspace is configured"
python3 publisher.py

