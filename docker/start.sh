#!/bin/bash
if [ ! -f "config.txt" ] 
then
  echo "Enter seed phrase. It won't be visible!"
  read -s seed
  read -p "Save config? y/n" answer
  if [[ $answer = y ]] ; 
  then
    echo $seed > ./config.txt
    echo "Config file is saved"
  fi
else
  seed=$(<config.txt)
fi
SEED="$seed" docker-compose up