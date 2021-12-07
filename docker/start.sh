#!/bin/bash
DEVICE_ID=""
if [[ ! $(docker -v) ]]
then
    echo "You need to install docker first. Check https://docs.docker.com/engine/install/"
    exit 1
fi
if [[ ! $(git --version) ]]
then
    echo "You need to install git first. Check https://github.com/git-guides/install-git"
    exit 1
fi
if [ ! -d "./rws" ] 
then 
    echo "Configuring workspace. It may take a few minutes."
    git clone https://github.com/tubleronchik/rws.git
fi
cd rws/docker
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