##Generate Topic Dialogs
import boto3
import json

def generatePayload(feed_item):
    feed_item_json = json.loads(feed_item)
    text = feed_item_json['text']
    payload = """Command: Discuss the following content in the form of a short casual podcast conversation between 2 hosts named Richard and Li.  
Because this is one of many topics, do not close out the conversation and do not greet the other host.  

Here is the content: """ + text
    
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

def write_object(bucket,feeditem,dialog,run_id,s3):
    feed_item_json = json.loads(feeditem)
    itemId = feed_item_json['id']
    s3object = s3.Object(bucket, run_id + '/dialogs/'+itemId+'.json')
    s3object.put(Body=json.dumps(dialog))
    manifestObject = {
    "itemId": itemId,
    "bucket": s3object.bucket_name,
    "key": s3object.key,
    "runId": run_id
    }
    return s3object,manifestObject

def lambda_handler(event, context):
    try:
        print("Event Data:")
        print(event)
        bucketname = event['Result']['metadata']['bucket']
        key = event['Result']['metadata']['key']
        runId = event['runId']
        endpoint = event['llmEndpoint']
        bedrockRegion = event['bedrockRegion']
        modelId = event['modelId']

        bedrock = boto3.client('bedrock', bedrockRegion, endpoint_url=endpoint)
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucketname)
        feeditem = bucket.Object(key).get()['Body'].read().decode()
        print('runId is: ' + runId)
        payload = generatePayload(feeditem)
        dialog = createDialog(payload,bedrock,modelId)
        response = write_object(bucketname,feeditem,dialog,runId,s3)
        print(response[1])
        return response[1]
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'Error occurred'