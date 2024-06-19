#!/bin/bash

echo "dongbuict0" | sudo -S apt-get update
sudo apt-get install -y python3-pip
sudo apt-get install python3.8-venv

sudo -H pip install -U jetson-stats

sudo dpkg -i install/nomachine_8.11.3_3_arm64.deb

