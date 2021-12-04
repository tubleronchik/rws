#!/bin/bash
if [ ! -d "./rws-main" ] 
then 
    echo "Configuring workspace. It may take a few minutes. You may need to enter your password."
    sudo apt update > /dev/null 2>&1
    sudo apt install python3-pip
    sudo apt-get install zip unzip
     sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io
    sudo apt-get install docker-compose
    wget https://github.com/tubleronchik/rws/archive/main.zip > /dev/null 2>&1
    unzip main.zip > /dev/null 2>&1
    echo "Done"
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
    echo "Config file is saved"
  fi
else
  seed=$(<config.txt)
fi
sudo SEED="$seed" docker-compose up
