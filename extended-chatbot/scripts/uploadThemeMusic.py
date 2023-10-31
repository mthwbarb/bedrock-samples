import sys
import boto3

n = len(sys.argv)
if n < 2:
    print ("Must have 1 argument: s3BucketName")
    print (sys.argv[0])
    quit()

s3 = boto3.resource('s3')
 
bucket = s3.Bucket(sys.argv[1])
with open('./audio/theme_short.mp3', 'rb') as data:
    bucket.upload_fileobj(data, 'themes/theme_short.mp3')
with open('./audio/theme_long.mp3', 'rb') as data:
    bucket.upload_fileobj(data, 'themes/theme_long.mp3')
