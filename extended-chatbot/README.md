# namer-hackathon
# Team Atlantis
# Extended Chat Bot

A chat bot application backed by Amazon Bedrock and Amazon Kendra.  Demonstrates how to extend Generative AI capabilities beyond a simple chat bot by
allowing end users to consume the information via the medium of their choosing.
You have the option of generating a Podcast, PowerPoint presentation, or a job listing.

Deployment tested via AWS Cloud9 running Amazon Linux 2 in us-east-1.  Uses Amazon Bedrock in us-east-1.

## Pre-Reqs

1. AWS CLI
2. AWS SAM CLI   see https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. Python 3.11 (If using Amazon Linux 2 on Cloud9 which only has support for 3.7 and 3.8, you can run the included `./scripts/updatePython.sh` script to install, make sure to `chmod 777 ./scripts/updatePython.sh` first)
* Note: If you use AWS Cloud9, steps 1, and 2 above are already preinstalled.
4. An account with access to Bedrock and 3p Models (Anthropic Claude v2). An IAM policy attached to the entity running the Streamlit aplication is also required (See `bedrockPolicy.json`)  
5. If using Cloud9, you need to attach an IAM role to the EC2 instance with permissions to Bedrock (and other services). THen go to AWS Settings-->Credentials and turn off AWS Managed Temp Credentials.  You may need to stop/start the instance to apply.  You also need to allow Streamlit traffic in the attached security group (TCP port 8501).
6. If using Cloud9, you should increase the EBS voume size.  Run the included `scripts/cloud9-resize.sh` script and resize to at least 50GB.

## Instructions

1. Run `./scripts/setup.sh` to install additional prerequisites including the boto3 SDK which includes Bedrock.
2. Navigate to the SAM folder `cd SAM`
3. Build the SAM package `sam build`
4. Deploy the package.`sam deploy --capabilities CAPABILITY_NAMED_IAM --guided`  Give your stack a name, and use the region where Bedrock is deployed.  Use the defaults for the rest of the options.
5. The following resources will be deployed: Lambda Function, Kendra Index.  This will take some time due to Kendra.
6. Note the outputs from the SAM deployment, you will need the Lambda Function names, the S3 bucket name, and the Kendra Index ID for subsequent steps.
7. Navigate up one folder `cd ..`
8. Load the AWS Blogs data into Kendra.  The RSS feed list is stored in `feeds.json`.  Run `python3.11 ./scripts/loadData.py <kendraIndexId>`.  Substitue <kendraIndexId> with the ID that you copied from the SAM deployment output in step 4.
9. Run `python uploadThemeMusic.py <bucketName>` with the bucket from the stack to copy the files in the `audio` to the bucket into the `themes/` prefix.
10. Navigate to the `streamlit` folder. `cd streamlit`
11. Open `streamlitapp.py` with your editor and update the 5 variables using the outputs from step 4.
12. Run the Streamlit app using the Bedrock Claudev2 model. `streamlit run streamlitapp.py bedrock_claudev2`
13. Open the provided URL and start chatting.
