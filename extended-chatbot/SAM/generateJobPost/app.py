
import json
import boto3
import os


def generatePayload(bucket,uuid):
    print("getting chat history: "+ 'chats/'+uuid+'.json')
    chatObject = bucket.Object('chats/'+uuid+'.json').get()['Body'].read().decode('utf-8')
    chatObject_json = str(json.loads(chatObject))
    payload = """\n\nHuman:We are a luxury retail company called AnyCompany, headquartered in NYC.   
    Our brand is one of the top 5 most recognized apparel brands on the globe.  
    Please create a job posting in LinkedIn format based on the following job description.  Include specific call-outs to the AWS services mentioned: """+chatObject_json+"""\n\nAssistant:"""
    return payload


def generateJobPost(payload,client,modelId,uuid,s3Client,bucket):
    try:
        print("Invoking Endpoint")
        body = json.dumps({"prompt": payload, "max_tokens_to_sample": 2048, "temperature": 1, "top_k": 250, "top_p":0.999, "stop_sequences": ["\\n\\nHuman:","\\n\\nhuman:"]})
        accept = "application/json"
        contentType = "application/json"
        try:
            response = client.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get("body").read())
            output = response_body.get("completion")
            print(output)
            with open('/tmp/output.txt', 'w') as f:
                f.write(output)
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            return 'Error occurred:'
        print('Uploading job listing text file to s3: ' + 'jobs/'+uuid+'.txt')
        s3=s3Client
        s3.meta.client.upload_file('/tmp/output.txt',bucket,'jobs/'+uuid+'.txt')
        #cleanup
        print("Cleaning Up temp file")
        os.remove("/tmp/output.txt")
        return 'jobs/'+uuid+'.txt'
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return "Error creating job listing"
def lambda_handler(event, context):
    try:
        print("Starting...")
        print(event)
    
        bucketname = event['bucket']
        uuid = event['uuid']
        bedrockRegion = 'us-east-1'
        modelId = event['modelId']
        
    
        #print("runId: " +runId)
        print("Bucket: "+bucketname)
        bedrock = boto3.client('bedrock-runtime', bedrockRegion)
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucketname)

        print("Generating Payload for LLM")
        payload = generatePayload(bucket,uuid)
        print("Sending Payload to LLM and generating the job posting:" + payload)
        jobListingObject = generateJobPost(payload,bedrock,modelId,uuid,s3,bucketname)
        return jobListingObject
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'Error occurred:'
