import json
import boto3
BEDROCK_REGION='us-east-1'
boto3_bedrock = boto3.client(service_name='bedrock-runtime',region_name=BEDROCK_REGION)
prompt_data = """\n\nHuman: Provide a short python hello world script.

\n\nAssistant:
"""

body = json.dumps({"prompt": prompt_data, "max_tokens_to_sample": 500})
modelId = "anthropic.claude-v2"  # change this to use a different version from the model provider
accept = "application/json"
contentType = "application/json"

response = boto3_bedrock.invoke_model(
    body=body, modelId=modelId, accept=accept, contentType=contentType
)
response_body = json.loads(response.get("body").read())

print(response_body.get("completion"))

