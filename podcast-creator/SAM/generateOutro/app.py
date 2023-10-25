import boto3
import json
import os
from datetime import date
import re


def generatePayload(date):
    #construct the prompt
    payload = """\n\nHuman: Write an outro for a podcast called The AWS Factor.  
    You are the host named Richard and your co-host is named Li.  The Podcast theme is "Latest announcements from AWS".  
    Include some off topic banter between the hosts. Remind audience to check out the AWS news Blog. End with something similar to 'See you next week'.
    \n\nAssistant:"""
    return payload

def createDialog(payload,client,modelId):
    print("Invoking Endpoint")
    body = json.dumps({"prompt": payload, "max_tokens_to_sample": 1024, "temperature": 1, "top_k": 250, "top_p":0.999})
    accept = "application/json"
    contentType = "application/json"
    response = client.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get("body").read())
    output = response_body.get("completion")
    print(output)
    sentences_list = [y for y in (x.strip() for x in output.splitlines()) if y]
    dialog=[]
    i=1
    print("Generating Sentence List")
    for sentence in sentences_list:
        print(sentence)
        #Skip over non-speech sentences
        try:
            sentence_voice = sentence.rsplit(': ', 1)[0]
            sentence_content = sentence.rsplit(': ', 1)[1]
            dialog.append({"seq":i, "voice":sentence_voice, "content":sentence_content})
            i=i+1
        except:
            print("There doesnt appear to be a voice indicator, skipping.")
    return dialog

def generateAudio(payload,run_id,bucket,s3Client,region):
    #load the sentences from the s3 object
    s3=s3Client
    print("initiating Polly session")
    polly_client = boto3.client('polly',region)
    for sentence in payload:
        if sentence["voice"] == "Richard":
            print('Generating audio snippet for sequence #: ' + str(sentence["seq"]) + '.  Sentence: ' + sentence["content"])
            response = polly_client.synthesize_speech(VoiceId='Stephen',
                            OutputFormat='mp3', 
                            Text = sentence["content"],
                            Engine = 'neural')
            
            #append the bits to existing mp3
            file = open('/tmp/output.mp3', 'ab+')
            file.write(response['AudioStream'].read())
            file.close()
        else:
            print('Generating audio snippet for sequence #: ' + str(sentence["seq"]) + '.  Sentence: ' + sentence["content"])
            response = polly_client.synthesize_speech(VoiceId='Ruth',
                            OutputFormat='mp3', 
                            Text = sentence["content"],
                            Engine = 'neural')
            
            #append the bits to existing mp3
            file = open('/tmp/output.mp3', 'ab+')
            file.write(response['AudioStream'].read())
            file.close()
    #upload the mp3 object to s3
    print('Uploading mp3 file to s3: ' + run_id + '/other_audio/outro.mp3')
    s3.meta.client.upload_file('/tmp/output.mp3',bucket,run_id + '/other_audio/outro.mp3')
    #cleanup
    os.remove("/tmp/output.mp3")

    return 

def lambda_handler(event, context):
    try:
        print("Starting...")
        print(event)
    
        bucketName = event['bucket']
        runId = event['uuid']
        endpoint = event['llmEndpoint']
        bedrockRegion = event['bedrockRegion']
        modelId = event['modelId']
        
        print("runId: " +runId)
        print("Bucket: "+bucketName)
        bedrock = boto3.client('bedrock-runtime', bedrockRegion, endpoint_url=endpoint)
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucketName)
        
        today = date.today()
        todayDate = today.strftime("%B %d, %Y")
        
        print("Generating Payload for LLM")
        payload = generatePayload(todayDate)
        print(payload)
        print("Sending Payload to LLM and generating the dialog")
        dialog = createDialog(payload,bedrock,modelId)
        print(dialog)
        print("Generating audio file")
        generateAudio(dialog,runId,bucketName,s3,bedrockRegion)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'Error occurred'