import boto3
from collections import Counter
from datetime import datetime, timedelta
import json

BUCKET = 'wjrm500-spotify'
OBJECT_KEY = 'play-history'
s3 = boto3.client('s3')

def handler(event, context):
    print('Getting listen history from S3...')
    obj = s3.get_object(Bucket = BUCKET, Key = OBJECT_KEY)
    listen_history = json.loads(obj['Body'].read().decode('utf-8'))
    one_week_ago = datetime.now() - timedelta(days = 7)
    last_week_listens = [x for x in listen_history if datetime.strptime(x['datetime'], '%Y-%m-%d %H:%M:%S') > one_week_ago]
    artist_plays = Counter([x['artist'] for x in last_week_listens])
    top_artists = artist_plays.most_common(5)
    email_content = 'Your five most played artists over the past week are:\n' + '\n'.join(x[0] + ': ' + str(x[1]) for x in top_artists)