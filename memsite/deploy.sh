#!/bin/sh

cd /home/ubuntu/app
pyenv global ec2_deploy
pip3 install -r requirements.txt
pip3 install --upgrade pip
python3 manage.py runserver 0:8080