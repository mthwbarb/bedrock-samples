#!/bin/sh

set -e

echo "Installing helper tools"
sudo yum update -y
sudo yum -y install jq bash-completion
python3.11 -m pip install wheel boto3>=1.28.57 streamlit


#Update SAM cli
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install --update


