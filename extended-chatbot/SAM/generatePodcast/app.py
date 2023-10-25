#generate a segment intro for each unique category

from pydub import AudioSegment

import boto3
import json
import os

print(boto3.__version__)

# How many ms before the end of the podcast to begin theme music crossfade
OUTRO_OVERLAP_MS = 7000

def generatePayload(bucket,uuid):
    print("getting chat history: "+ 'chats/'+uuid+'.json')
    chatObject = bucket.Object('chats/'+uuid+'.json').get()['Body'].read().decode('utf-8')
    chatObject_json = str(json.loads(chatObject))
    payload = """\n\nHuman:Given the following conversation between a human and an AI about AWS services provided in json format, generate a script for a podcast 
    called "The AWS Factor" with 2 hosts named Richard and Li.  Include a brief introduction before discussing the topics.
    Provide the output in the following format:
    Richard:
    Li:
    "

conversation: """ + chatObject_json + """\n\nAssistant:"""
    
    return payload

def createDialog(payload,client,modelId):
    print("Invoking Endpoint")
    body = json.dumps({"prompt": payload, "max_tokens_to_sample": 2048, "temperature": 1, "top_k": 250, "top_p":0.999})
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

    # Add music credits
    dialog[-1]["content"] += ' Theme music composed by AWS DeepComposer.'
    return dialog

def addThemeMusic(podcast_path, bucketname, s3):
    
    bucket = s3.Bucket(bucketname)
    intro_file = open('/tmp/theme_short.mp3', 'wb')

    intro_file.write(bucket.Object('themes/theme_short.mp3').get()['Body'].read())
    intro_file.close()
    intro = AudioSegment.from_mp3('/tmp/theme_short.mp3')

    cast = AudioSegment.from_mp3(podcast_path)

    outro_file = open('/tmp/theme_long.mp3', 'wb')
    outro_file.write(bucket.Object('themes/theme_long.mp3').get()['Body'].read())
    outro_file.close()
    outro = AudioSegment.from_mp3('/tmp/theme_long.mp3')

    start = intro + cast[:len(cast)-OUTRO_OVERLAP_MS]
    overlap = outro[:OUTRO_OVERLAP_MS].overlay(cast[len(cast)-OUTRO_OVERLAP_MS:], position=0, gain_during_overlay=-12)
    end = outro[OUTRO_OVERLAP_MS:]

    final = start + overlap + end

    final.export(podcast_path, format="mp3")
    os.remove("/tmp/theme_short.mp3")
    os.remove("/tmp/theme_long.mp3")


def generateAudio(payload,run_id,bucket,s3Client,region):
    #setup Polly client
    print("initiating Polly session")
    polly_client = boto3.client('polly',region)
    #Syntesize audio from the input

    for sentence in payload:
        if sentence["voice"].lower() == "richard":
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
    
    addThemeMusic('/tmp/output.mp3', bucket, s3Client)

    #upload the mp3 object to s3
    print('Uploading mp3 file to s3: ' + 'podcasts/'+run_id+'.mp3')
    s3=s3Client
    s3.meta.client.upload_file('/tmp/output.mp3',bucket,'podcasts/'+run_id+'.mp3')
    #cleanup
    print("Cleaning Up temp file")
    os.remove("/tmp/output.mp3")
    
    #prepare output for step function

    return 'podcasts/'+run_id+'.mp3'
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
        print("Sending Payload to LLM and generating the dialog:" + payload)
        dialog = createDialog(payload,bedrock,modelId)
        print(dialog)
        print("Generating audio file")
        mp3Object = generateAudio(dialog,uuid,bucketname,s3,bedrockRegion)
        return mp3Object
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'Error occurred:'
