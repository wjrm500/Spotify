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
        print('Getting listen history from S3...')
        obj = s3.get_object(Bucket = BUCKET, Key = OBJECT_KEY)
        listen_history = json.loads(obj['Body'].read().decode('utf-8'))
        print('Updating listen history...')
        update_listen_history(listen_history, recent_listens)
    except ClientError as e:
        if e.response.get('Error').get('Code') == 'NoSuchKey':
            print(f'No object found in bucket {BUCKET} with key {OBJECT_KEY}, creating new object...')
            put_listen_history(recent_listens)
        else:
            print('Unknown client error')
            raise e    

def put_listen_history(recent_listens):
    body = json.dumps(recent_listens).encode('utf-8')
    try:
        s3.put_object(Bucket = BUCKET, Key = OBJECT_KEY, Body = body)
        print(f'Recent listens successfully added to new object {OBJECT_KEY} in S3 bucket {BUCKET}')
    except ClientError:
        print('Unknown client error')

def update_listen_history(listen_history, recent_listens):
    listen_history_listen_ids = [x['listen_id'] for x in listen_history]
    listens_added = 0
    for recent_listen in recent_listens:
        if recent_listen['listen_id'] not in listen_history_listen_ids:
            listen_history.insert(0, recent_listen)
            listens_added += 1
    body = json.dumps(listen_history).encode('utf-8')
    s3.put_object(Bucket = BUCKET, Key = OBJECT_KEY, Body = body)
    print(f'{listens_added} new listens added!')