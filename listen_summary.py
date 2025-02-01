import os
import json
import functools
from collections import Counter
from datetime import datetime, timedelta
from enum import Enum
from os.path import dirname, abspath
import jinja2 as jj2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration via environment variables
PLAY_HISTORY_FILE = os.environ.get("PLAY_HISTORY_FILE", "/data/spotify-play-history.json")
EMAIL = os.environ.get("EMAIL", "your-email@example.com")

how_many = 50

class ListenField(str, Enum):
    ARTIST = "artist"
    ALBUM = "album"
    SONG = "song"

class TimeFrame(str, Enum):
    LAST_WEEK = "the past seven days"
    ALL_TIME = "all time"

@functools.lru_cache(maxsize=None)
def get_listen_history():
    print("Getting listen history from local file...")
    if not os.path.exists(PLAY_HISTORY_FILE):
        print("Play history file does not exist, returning empty list.")
        return []
    with open(PLAY_HISTORY_FILE, "r", encoding="utf-8") as f:
        listen_history = json.load(f)
    return listen_history

def get_all_time_top_x(listen_history, x: ListenField):
    return Counter([listen[x] for listen in listen_history]).most_common(how_many)

def get_last_week_top_x(listen_history, x: ListenField):
    one_week_ago = datetime.now() - timedelta(days=7)
    last_week_listens = [
        listen for listen in listen_history 
        if datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > one_week_ago
    ]
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
    environment = jj2.Environment(loader=jj2.FileSystemLoader(dirname(abspath(__file__))))
    template = environment.get_template("email_template.html")
    data = denumify_dict(data)
    return template.render(**data)

def get_text_content(data):
    last_week_top_artists = data[ListenField.ARTIST][TimeFrame.LAST_WEEK]
    all_time_top_artists = data[ListenField.ARTIST][TimeFrame.ALL_TIME]
    last_week_top_albums = data[ListenField.ALBUM][TimeFrame.LAST_WEEK]
    all_time_top_albums = data[ListenField.ALBUM][TimeFrame.ALL_TIME]
    last_week_top_songs = data[ListenField.SONG][TimeFrame.LAST_WEEK]
    all_time_top_songs = data[ListenField.SONG][TimeFrame.ALL_TIME]
    text_content = """
        Your {} most played artists over the past week are:\n{}
        Your {} most played artists of all time are:\n{}
        Your {} most played albums over the past week are:\n{}
        Your {} most played albums of all time are:\n{}
        Your {} most played songs over the past week are:\n{}
        Your {} most played songs of all time are:\n{}
    """.format(
        len(last_week_top_artists),
        "\n".join("{}: {}".format(x[0], str(x[1])) for x in last_week_top_artists),
        len(all_time_top_artists),
        "\n".join("{}: {}".format(x[0], str(x[1])) for x in all_time_top_artists),
        len(last_week_top_albums),
        "\n".join("{}: {}".format(x[0], str(x[1])) for x in last_week_top_albums),
        len(all_time_top_albums),
        "\n".join("{}: {}".format(x[0], str(x[1])) for x in all_time_top_albums),
        len(last_week_top_songs),
        "\n".join("{}: {}".format(x[0], str(x[1])) for x in last_week_top_songs),
        len(all_time_top_songs),
        "\n".join("{}: {}".format(x[0], str(x[1])) for x in all_time_top_songs)
    )
    text_content = text_content.strip()
    return "\n".join(map(str.strip, text_content.split("\n")))

def generate_email():
    data = get_data()
    return {
        "subject": get_email_subject(data[ListenField.ARTIST][TimeFrame.LAST_WEEK]),
        "html_content": get_html_content(data),
        "text_content": get_text_content(data)
    }

def send_email(email):
    # Using smtplib to send email via localhost (Postfix)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = email["subject"]
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    part1 = MIMEText(email["text_content"], "plain")
    part2 = MIMEText(email["html_content"], "html")
    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP("localhost") as server:
        server.sendmail(EMAIL, [EMAIL], msg.as_string())
    print("Email sent successfully.")

def preview():
    email = generate_email()
    with open("email.html", "w", encoding="utf-8") as f:
        f.write(email["html_content"])
    print("Preview written to email.html.")

def main():
    email = generate_email()
    send_email(email)

if __name__ == "__main__":
    main()
