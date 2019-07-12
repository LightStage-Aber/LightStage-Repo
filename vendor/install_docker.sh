#!/bin/bash
#
# Docker install script:
#
echo 
echo "The LightStage Tool's web interface for hardware-simulation communication uses 'redis' on 'Docker' to share real-time data."
echo 
echo "This script will:"
echo 
echo "(1) download the docker install script via https://get.docker.com"
echo "(2) execute that script"
echo "(3) add the current user to the docker group."
echo "After completion, to run docker commands as your current user (i.e. without sudo) you will need to log-out and log-in again."
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker $USER
echo "------------"
echo "Please log-out and log-in to permit running redis on docker as your current user (i.e. without sudo)"
echo "------------"

