import boto3
import json

def generate_podcast(bucket,chat_history,user_id,lambdaFunction,modelId):
    s3=boto3.resource('s3')
    lambda_client = boto3.client('lambda','us-east-1')

    chatHistObject = {
    "uuid": user_id,
    "chat_history": chat_history
    }
    try:
        s3object = s3.Object(bucket, 'chats/'+user_id+'.json')
        s3object.put(Body=json.dumps(chatHistObject))
        lambda_payload = {
            "s3Object":"/chats/"+user_id+'.json',
            "bucket":bucket,
            "modelId":modelId,
            "uuid":user_id
        }
        mp3Object = lambda_client.invoke(FunctionName=lambdaFunction, 
                             InvocationType='RequestResponse',
                             Payload=json.dumps(lambda_payload)
                             )
        #st.write(json.loads(mp3Object["Payload"].read()))
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucket)
        audio = bucket.Object(json.loads(mp3Object["Payload"].read())).get()
        audioStream = audio['Body'].read()
        return audioStream
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'error'

def generate_pptx(bucket,chat_history,user_id,lambdaFunction,modelId):
    s3=boto3.resource('s3')
    lambda_client = boto3.client('lambda','us-east-1')
    chatHistObject = {
    "uuid": user_id,
    "chat_history": chat_history
    }
    try:
        s3object = s3.Object(bucket, 'chats/'+user_id+'.json')
        s3object.put(Body=json.dumps(chatHistObject))
        lambda_payload = {
            "s3Object":"/chats/"+user_id+'.json',
            "bucket":bucket,
            "modelId":modelId,
            "uuid":user_id
        }
        pptxObject = lambda_client.invoke(FunctionName=lambdaFunction, 
                     InvocationType='RequestResponse',
                     Payload=json.dumps(lambda_payload)
                     )
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucket)
        presentation = bucket.Object(json.loads(pptxObject["Payload"].read())).get()
        presentationStream = presentation['Body'].read()
        return presentationStream
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'error'
def generate_jobPost(bucket,chat_history,user_id,lambdaFunction,modelId):
    s3=boto3.resource('s3')
    lambda_client = boto3.client('lambda','us-east-1')
    chatHistObject = {
    "uuid": user_id,
    "chat_history": chat_history
    }
    try:
        s3object = s3.Object(bucket, 'chats/'+user_id+'.json')
        s3object.put(Body=json.dumps(chatHistObject))
        lambda_payload = {
            "s3Object":"/chats/"+user_id+'.json',
            "bucket":bucket,
            "modelId":modelId,
            "uuid":user_id
        }
        pptxObject = lambda_client.invoke(FunctionName=lambdaFunction, 
                     InvocationType='RequestResponse',
                     Payload=json.dumps(lambda_payload)
                     )
        s3=boto3.resource('s3')
        bucket = s3.Bucket(bucket)
        jobPost = bucket.Object(json.loads(pptxObject["Payload"].read())).get()
        jobPostStream = jobPost['Body'].read()
        return jobPostStream
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        return 'error'
               