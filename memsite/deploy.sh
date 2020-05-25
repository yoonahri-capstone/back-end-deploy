#!/bin/sh

cd /home/ubuntu/app
rm -rf __pycache__/
cd memsite
rm -rf __pycache__/
# pyenv global ec2_deploy
# pip3 install -r requirements.txt
# pip3 install --upgrade pip
cd ..
python3 manage.py runserver 0:8080