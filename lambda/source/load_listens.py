import boto3
from botocore.exceptions import ClientError
import json

from Spotify import Spotify

BUCKET = 'wjrm500-spotify'
OBJECT_KEY = 'play-history'
spotify = Spotify()
s3 = boto3.client('s3')

def s3_handler(event, context):
    recent_listens = spotify.get_recent_listens()
    try:
        obj = s3.get_object(Bucket = BUCKET, Key = OBJECT_KEY)
    except ClientError as e:
        if e.response.get('Error').get('Code') == 'NoSuchKey':
            print(f'No object found in bucket {BUCKET} with key {OBJECT_KEY}')
            put_play_history(recent_listens)
        else:
            print('Unknown client error')
            raise e
    update_play_history(obj['Body'], recent_listens)

def put_play_history(recent_listens):
    body = json.dumps(recent_listens).encode('utf-8')
    try:
        s3.put_object(Bucket = BUCKET, Key = OBJECT_KEY, Body = body)
        print(f'Recent listens successfully added to new object {OBJECT_KEY} in bucket {BUCKET}')
    except ClientError:
        print('Unknown client error')

def update_play_history(play_history, recent_listens):
    pass