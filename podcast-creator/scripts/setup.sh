#!/bin/sh

set -e

echo "Installing helper tools"
sudo yum update -y
sudo yum -y install jq bash-completion
python3.11 -m pip install wheel boto3 streamlit


#Update SAM cli
wget -O /tmp/aws-sam-cli-linux-x86_64.zip https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip /tmp/aws-sam-cli-linux-x86_64.zip -d /tmp/sam-installation
sudo /tmp/sam-installation/install --update
