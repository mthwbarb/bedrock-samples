#Processes an RSS feed, grabs the title and conten, and stores in Kendra
import feedparser
from datetime import datetime, timedelta
from dateutil.parser import parse
import json
import boto3
import os
import requests
import re
import sys



def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    cleaned =  re.sub(clean, '', text)
    return cleaned.replace("\n", "")

n = len(sys.argv)
if n < 2:
    print ("Must have 1 argument: kendraIndexId")
    print (sys.argv[0])
    quit()
print("Kendra In")
index_id = str(sys.argv[1])
kendra = boto3.client("kendra",region_name = 'us-east-1')
feedsListLocal = open("feeds.json", "r")
feedsList_json = feedsListLocal.read()
feedsList = json.loads(feedsList_json)
documents = []
for feed in feedsList:
    url = feed.get('url')
    feedObject = feedparser.parse(url)
    for entry in feedObject.entries:
        print('Processing Entry: '+entry.title)
        date = parse(entry.published)
        isodate = date.isoformat()
        document = {
            "Id": entry.id,
            "Blob": remove_html_tags(entry.content[0].get('value')),
            "ContentType": "PLAIN_TEXT",
            "Title": entry.title,
            "Attributes": [ 
            { 
               "Key": "_created_at",
               "Value": { 
                  "DateValue": isodate
               }
            },
            {
                "Key": "_source_uri",
                "Value": {
                    "StringValue": entry.link
                }
            }
            ],
        }
        print("Object Uploaded")
        documents = [
            document
        ]
        result = kendra.batch_put_document(
            IndexId = index_id,
            Documents = documents
        )

        print(result)  
