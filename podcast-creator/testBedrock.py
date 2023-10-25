import json
import boto3

BEDROCK_REGION='us-east-1'
BEDROCK_ENDPOINT = 'https://bedrock.us-east-1.amazonaws.com'
boto3_bedrock = boto3.client('bedrock', BEDROCK_REGION, endpoint_url=BEDROCK_ENDPOINT)
prompt_data = """Command: Discuss the following content in the form of a short casual podcast conversation between 2 hosts named Richard and Li.  
Because this is one of many topics, do not close out the conversation and do not greet the other host.  

Here is the content: You can now subscribe Amazon Simple Queue Service (SQS) Standard queues to Amazon Simple Notification Service (SNS) First-In-First-Out (FIFO) topics. Thus, from a single SNS FIFO topic, you can now deliver messages to SQS Standard queues, which offer best-effort ordering and at-least-once delivery, as well as to SQS FIFO queues, which support strict ordering and exactly-once delivery. This new capability further decouples message publishers from subscribers, as the SNS topic type no longer dictates the SQS queue type that subscribers ought to use.Amazon SNS is a messaging service for Application-to-Application (A2A) and Application-to-Person (A2P) communication. The A2A functionality provides topics for high-throughput, push-based, many-to-many messaging between distributed systems, microservices, and event-driven serverless applications. SNS Standard topics provide best-effort ordering and at-least-once-delivery, while SNS FIFO topics support strict ordering and exactly-once delivery. Both Standard and FIFO topics support message fan-out to multiple subscriptions, with high durability, security, and message filtering.SNS FIFO message delivery to SQS Standard queues is available in all AWS Regions, except for AWS GovCloud (US) Regions.To learn more, see:

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

