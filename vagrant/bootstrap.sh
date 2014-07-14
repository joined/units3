#!/usr/bin/env bash

# Install italian language pack
sudo apt-get install -y language-pack-it
# Install pip, git, and lxml dependencies
sudo apt-get install -y python3-pip libxml2-dev libxslt1-dev python3.4-dev zlib1g-dev git
# Install virtualenv via pip
sudo pip3 install virtualenv
# Cd home directory
cd /home/vagrant/
# Clone git repository
git clone https://github.com/joined/units3.git
# Cd cloned repo
cd units3
# Setup everything
./setup.sh
# Run
./run.py