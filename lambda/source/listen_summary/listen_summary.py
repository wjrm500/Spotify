import boto3
from collections import Counter
from datetime import datetime, timedelta
import jinja2 as jj2
import json
import os
from os.path import dirname, abspath

BUCKET = 'wjrm500-spotify'
OBJECT_KEY = 'play-history'
s3 = boto3.client('s3')
ses = boto3.client('ses')

def get_listen_history():
    print('Getting listen history from S3...')
    obj = s3.get_object(Bucket = BUCKET, Key = OBJECT_KEY)
    listen_history = json.loads(obj['Body'].read().decode('utf-8'))
    return listen_history

def get_all_time_top_artists(listen_history):
    return Counter([x['artist'] for x in listen_history]).most_common(25)

def get_last_week_top_artists(listen_history):
    one_week_ago = datetime.now() - timedelta(days = 7)
    last_week_listens = [x for x in listen_history if datetime.strptime(x['datetime'], '%Y-%m-%d %H:%M:%S') > one_week_ago]
    return Counter([x['artist'] for x in last_week_listens]).most_common(25)

def get_email_subject(last_week_top_artists):
    return 'Your Spotify weekly digest - featuring {}, {} and {}'.format(
        last_week_top_artists[0][0],
        last_week_top_artists[1][0],
        last_week_top_artists[2][0]
    )

def get_html_content(last_week_top_artists, all_time_top_artists):
    environment = jj2.Environment(loader = jj2.FileSystemLoader(dirname(abspath(__file__))))
    template = environment.get_template('email_template.html')
    return template.render(
        x = [
            ('over the past seven days', last_week_top_artists),
            ('of all time', all_time_top_artists)
        ]
    )

def get_text_content(last_week_top_artists, all_time_top_artists):
    return 'Your {} most played artists over the past week are:\n\n{}\n\nYour {} most played artists of all time are:{}'.format(
        len(last_week_top_artists),
        '\n'.join('{}: {}'.format(x[0], str(x[1])) for x in last_week_top_artists),
        len(all_time_top_artists),
        '\n'.join('{}: {}'.format(x[0], str(x[1])) for x in all_time_top_artists)
    )

def generate_email():
    listen_history = get_listen_history()
    all_time_top_artists = get_all_time_top_artists(listen_history)
    last_week_top_artists = get_last_week_top_artists(listen_history)
    return {
        'subject': get_email_subject(last_week_top_artists),
        'html_content': get_html_content(last_week_top_artists, all_time_top_artists),
        'text_content': get_text_content(last_week_top_artists, all_time_top_artists)
    }

def preview():
    email = generate_email()
    with open("email.html", "w") as f:
        f.write(email["html_content"])

def handler(event, context):
    email = generate_email()
    ses.send_email(
        Destination = {
            'ToAddresses': [os.environ.get('email')]
        },
        Message = {
            'Subject': {
                'Data': email["subject"]
            },
            'Body': {
                'Html': {
                    'Data': email["html_content"]
                },
                'Text': {
                    'Data': email["text_content"]
                }
            }
        },
        Source = os.environ.get('email')
    )

if __name__ == '__main__':
    preview()