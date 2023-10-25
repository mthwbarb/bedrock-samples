#generate a segment intro for each unique category

import boto3
import json
import os

def generatePayload(category):
    #grab the category friendly name
    catvalue = next(iter(category.values()))
    #construct the prompt
    payload = """\n\nHuman: Create a short conversation between 2 podcast hosts named Richard and Li.  The Podcast name is "The AWS Factor" and the theme is "What's new from AWS".  This is not the beginning of the show.  
    Do not mention previous discussion and do not go into any detail about the topic.  
    Rephrase: Now we are going to talk about """+catvalue+""" , so let's dive in.
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

def generateAudio(payload,run_id,category,bucket,s3Client,region):
    #grab the category id
    catkey = next(iter(category.keys()))
    #setup Polly client
    print("initiating Polly session")
    polly_client = boto3.client('polly',region)
    #Syntesize audio from the input

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
    print('Uploading mp3 file to s3: ' + run_id + '/transition_audio/'+catkey+'.mp3')
    s3=s3Client
    s3.meta.client.upload_file('/tmp/output.mp3',bucket,run_id + '/transition_audio/'+catkey+'.mp3')
    #cleanup
    print("Cleaning Up temp file")
    os.remove("/tmp/output.mp3")
    
    #prepare output for step function
    manifestObject = {"audioObjectKey": 'transition_audio/'+catkey+'.mp3'}
    return manifestObject
def lambda_handler(event, context):
    try:
        print("Starting...")
        print(event)
    
        bucketname = event['bucket']
        runId = event['uuid']
        endpoint = event['llmEndpoint']
        bedrockRegion = event['bedrockRegion']
        modelId = event['modelId']
    
        print("runId: " +runId)
        print("Bucket: "+bucketname)
        bedrock = boto3.client('bedrock-runtime', bedrockRegion, endpoint_url=endpoint)
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucketname)
        manifestObject = bucket.Object(runId + '/manifest.json').get()['Body'].read().decode('utf-8')
        manifestObject_json = json.loads(manifestObject)
        
        #Get list of unique categories from the manifest
        uniqueCategories = ( set(d['category'] for d in manifestObject_json) )
        #this is our mapping of category to Friendly category name
        category_map={
        "analytics":"Analytics",
        "application-services":"Application Integration",
        "blockchain":"Blockchain",
        "business-productivity":"Business Applications",
        "cost-management":"Cloud Financial Management",
        "compute":"Compute",
        "containers":"Containers",
        "customer-enablement":"Customer Enablement",
        "messaging":"Customer Engagement",
        "databases":"Database",
        "developer-tools":"Developer Tools",
        "desktop-and-app-streaming":"End User Computing",
        "mobile-services":"Front End Web and Mobile",
        "game-development":"GameTech",
        "internet-of-things":"Internet of Things",
        "artificial-intelligence":"Machine Learning",
        "management-and-governance":"Management and Governance",
        "media-services":"Media Services",
        "migration":"Migration and Transfer",
        "networking-and-content-delivery":"Networking and Content Delivery",
        "networking": "Networking and Content Delivery",
        "aws-marketplace-and-partners":"Partners",
        "quantum-technologies":"Quantum Technologies",
        "robotics":"Robotics",
        "satellite":"Satellite",
        "security-identity-and-compliance":"Security, Identity, and Compliance",
        "serverless":"Serverless",
        "storage":"Storage",
        "training-and-certification":"Training and Certification",
        "partner-network":"Partners",
        "general":"Other AWS Services"
        }
        uniqueCategoriesMap = []
        for category in uniqueCategories:
            item={}
            item[category] = category_map.get(category)
            uniqueCategoriesMap.append(item)
        #iterate through each category pair
        print(uniqueCategoriesMap)
        for category in uniqueCategoriesMap:
            print("Generating Payload for LLM")
            payload = generatePayload(category)
            print("Sending Payload to LLM and generating the dialog:" + payload)
            dialog = createDialog(payload,bedrock,modelId)
            print(dialog)
            print("Generating audio file")
            generateAudio(dialog,runId,category,bucketname,s3,bedrockRegion)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'Error occurred:'
