import boto3
from collections import Counter
from datetime import datetime, timedelta
import jinja2 as jj2
import json
import os

BUCKET = 'wjrm500-spotify'
OBJECT_KEY = 'play-history'
s3 = boto3.client('s3')
ses = boto3.client('ses')

def handler(event, context):
    print('Getting listen history from S3...')
    obj = s3.get_object(Bucket = BUCKET, Key = OBJECT_KEY)
    listen_history = json.loads(obj['Body'].read().decode('utf-8'))
    all_time_top_artists = Counter([x['artist'] for x in listen_history]).most_common(25)
    one_week_ago = datetime.now() - timedelta(days = 7)
    last_week_listens = [x for x in listen_history if datetime.strptime(x['datetime'], '%Y-%m-%d %H:%M:%S') > one_week_ago]
    last_week_top_artists = Counter([x['artist'] for x in last_week_listens]).most_common(25)


    email_subject = 'Your Spotify weekly digest - featuring {}, {} and {}'.format(
        last_week_top_artists[0][0],
        last_week_top_artists[1][0],
        last_week_top_artists[2][0]
    )

    # Getting HTML
    environment = jj2.Environment(loader = jj2.FileSystemLoader('.'))
    template = environment.get_template('email_template.html')
    html_content = template.render(
        x = [
            ('over the past seven days', last_week_top_artists),
            ('of all time', all_time_top_artists)
        ]
    )

    # Getting text
    text_content = 'Your {} most played artists over the past week are:\n\n{}\n\nYour {} most played artists of all time are:{}'.format(
        len(last_week_top_artists),
        '\n'.join('{}: {}'.format(x[0], str(x[1])) for x in last_week_top_artists),
        len(all_time_top_artists),
        '\n'.join('{}: {}'.format(x[0], str(x[1])) for x in all_time_top_artists)
    )

    resp = ses.verify_email_identity(EmailAddress = os.environ.get('email'))
    print(resp)
    resp = ses.send_email(
        Destination = {
            'ToAddresses': [os.environ.get('email')]
        },
        Message = {
            'Subject': {
                'Data': email_subject
            },
            'Body': {
                'Html': {
                    'Data': html_content
                },
                'Text': {
                    'Data': text_content
                }
            }
        },
        Source = os.environ.get('email')
    )
    print(resp)