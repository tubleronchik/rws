#!/bin/bash
DEVICE_ID=""
if [[ ! $(docker -v) ]]
then
    echo "You need to install docker first. Check https://docs.docker.com/engine/install/"
    exit 1
fi
if [ ! -d "./rws-main" ] 
then 
    echo "Configuring workspace. It may take a few minutes. You may need to enter your password"
    sudo apt-get install zip unzip
    wget https://github.com/tubleronchik/rws/archive/main.zip > /dev/null 2>&1
    unzip main.zip > /dev/null 2>&1
fi
cd rws-main/docker
if [ ! -f "config.txt" ] 
then
  echo "Enter seed phrase. It won't be visible!"
  read -s seed
  read -p "Save config? y/n " answer
  if [[ $answer = y ]] ; 
  then
    echo $seed > ./config.txt
  fi
else
  seed=$(<config.txt)
fi
SEED="$seed" DEVICE_ID="$DEVICE_ID" docker-compose up  