import boto3
from collections import Counter
from datetime import datetime, timedelta
import jinja2 as jj2
import json
import os
from enum import Enum
from os.path import dirname, abspath
import functools

BUCKET = "wjrm500-spotify"
OBJECT_KEY = "play-history"
s3 = boto3.client("s3")
ses = boto3.client("ses")

how_many = 5

class ListenField(str, Enum):
    ARTIST = "artist"
    ALBUM = "album"
    SONG = "song"

class TimeFrame(str, Enum):
    LAST_WEEK = "the past seven days"
    ALL_TIME = "all time"

@functools.lru_cache(maxsize=None)
def get_listen_history():
    print("Getting listen history from S3...")
    obj = s3.get_object(Bucket = BUCKET, Key = OBJECT_KEY)
    listen_history = json.loads(obj["Body"].read().decode("utf-8"))
    return listen_history

def get_all_time_top_x(listen_history, x: ListenField):
    return Counter([listen[x] for listen in listen_history]).most_common(how_many)

def get_last_week_top_x(listen_history, x: ListenField):
    one_week_ago = datetime.now() - timedelta(days = 7)
    last_week_listens = [listen for listen in listen_history if datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > one_week_ago]
    return Counter([listen[x] for listen in last_week_listens]).most_common(how_many)

def get_email_subject(last_week_top_artists):
    return "Your Spotify weekly digest - featuring {}, {} and {}".format(
        last_week_top_artists[0][0],
        last_week_top_artists[1][0],
        last_week_top_artists[2][0]
    )

def get_data():
    data = {}
    for field in ListenField:
        data[field] = {
            TimeFrame.LAST_WEEK: get_last_week_top_x(get_listen_history(), field),
            TimeFrame.ALL_TIME: get_all_time_top_x(get_listen_history(), field)
        }
    return data

def denumify_dict(d):
    if isinstance(d, dict):
        return {denumify_dict(k): denumify_dict(v) for k, v in d.items()}
    elif isinstance(d, Enum):
        return d.value
    else:
        return d

def get_html_content(data):
    environment = jj2.Environment(loader = jj2.FileSystemLoader(dirname(abspath(__file__))))
    template = environment.get_template("new_email_template.html")
    data = denumify_dict(data)
    return template.render(**data)

def get_text_content(data):
    return None

    # return "Your {} most played artists over the past week are:\n\n{}\n\nYour {} most played artists of all time are:{}".format(
    #     len(last_week_top_artists),
    #     "\n".join("{}: {}".format(x[0], str(x[1])) for x in last_week_top_artists),
    #     len(all_time_top_artists),
    #     "\n".join("{}: {}".format(x[0], str(x[1])) for x in all_time_top_artists)
    # )

def generate_email():
    data = get_data()
    return {
        "subject": get_email_subject(data[ListenField.ARTIST][TimeFrame.LAST_WEEK]),
        "html_content": get_html_content(data),
        "text_content": get_text_content(data)
    }

def preview():
    email = generate_email()
    with open("email.html", "w") as f:
        f.write(email["html_content"])

def handler(event, context):
    email = generate_email()
    ses.send_email(
        Destination = {
            "ToAddresses": [os.environ.get("email")]
        },
        Message = {
            "Subject": {
                "Data": email["subject"]
            },
            "Body": {
                "Html": {
                    "Data": email["html_content"]
                },
                "Text": {
                    "Data": email["text_content"]
                }
            }
        },
        Source = os.environ.get("email")
    )

if __name__ == "__main__":
    preview()