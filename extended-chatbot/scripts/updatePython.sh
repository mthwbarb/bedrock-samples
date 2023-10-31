#!/bin/sh

sudo yum update -y
sudo yum remove openssl-devel -y
sudo yum install gcc openssl11-devel bzip2-devel libffi-devel zlib-devel -y 
wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz -P /tmp
tar xzf /tmp/Python-3.11.4.tgz -C /tmp
cd /tmp/Python-3.11.4
sudo ./configure --enable-optimizations
sudo make altinstall
pip3.11 install --upgrade pip