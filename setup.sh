#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y
sudo apt-get clean

echo "Il est possible que certain packet ne se trouve plus dans le repository"
echo "Ne vous inquiéter pas , GOOGLE est LA !"
sleep 3

sudo apt-get install -y wiringpi python-picamera python cups cups pygame libjpeg
sudo pip install pil
