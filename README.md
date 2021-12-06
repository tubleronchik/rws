# RWS Script

## Requirements
- docker 
## Configuration file
Template for config file is stored in ``/dockere/config`` directory. Using this template, create file named ``config.json`` and add seed phrase for you account. 
## Get a package
```
git clone https://github.com/tubleronchik/rws
cd rws/docker
```
## Running
```
docker-compose up
```
## Optional
You can add device_id by running
```
DEVICE_ID="your_name" docker-compose up
```