#!/bin/sh

set -e

echo "Installing helper tools"
sudo yum update -y
sudo yum -y install jq bash-completion
python3.11 -m pip install wheel boto3 streamlit


echo "(Re)-creating directory"
rm -rf /tmp/dependencies
mkdir /tmp/dependencies
cd /tmp/dependencies
echo "Downloading dependencies"
curl -sS https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/bedrock-python-sdk.zip > sdk.zip
echo "Unpacking dependencies"
# (SageMaker Studio system terminals don't have `unzip` utility installed)
if command -v unzip &> /dev/null
then
    unzip sdk.zip && rm sdk.zip && echo "Done"
else
    echo "'unzip' command not found: Trying to unzip via Python"
    python3.11 -m zipfile -e sdk.zip . && rm sdk.zip && echo "Done"
fi
##Install custom boto3 SDK for Bedrock
python3.11 -m pip install --no-build-isolation --force-reinstall \
    /tmp/dependencies/awscli-*-py3-none-any.whl \
    /tmp/dependencies/boto3-*-py3-none-any.whl \
    /tmp/dependencies/botocore-*-py3-none-any.whl
#Update SAM cli
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install --update



