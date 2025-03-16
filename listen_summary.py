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

# Constants for item counts
WEEKLY_TOP_COUNT = 10
ALL_TIME_TOP_COUNT = 40

class ListenField(str, Enum):
    ARTIST = "artist"
    ALBUM = "album"
    SONG = "song"

class TimeFrame(str, Enum):
    LAST_WEEK = "the past seven days"
    ALL_TIME = "all time"

class ListenAnalyser:
    """Class for analysing listening history and generating statistics"""
    
    @staticmethod
    def get_listen_history():
        """Load listening history from file"""
        print("Getting listen history from local file...")
        if not os.path.exists(PLAY_HISTORY_FILE):
            print("Play history file does not exist, returning empty list.")
            return []
        with open(PLAY_HISTORY_FILE, "r", encoding="utf-8") as f:
            listen_history = json.load(f)
        return listen_history
    
    @staticmethod
    def get_past_year_start():
        """Get the date from exactly one year ago"""
        return datetime.now() - timedelta(days=365)
    
    @staticmethod
    def filter_by_timeframe(listen_history, timeframe):
        """Filter listening history by timeframe"""
        if timeframe == TimeFrame.ALL_TIME:
            return listen_history
        elif timeframe == TimeFrame.LAST_WEEK:
            one_week_ago = datetime.now() - timedelta(days=7)
            return [
                listen for listen in listen_history 
                if datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > one_week_ago
            ]
    
    @staticmethod
    def get_artist_stats(listen_history, limit):
        """Generate artist statistics with past year count"""
        # Get basic counts
        artist_counter = Counter([listen["artist"] for listen in listen_history])
        top_artists = artist_counter.most_common(limit)
        
        # Get past year start date
        past_year_start = ListenAnalyser.get_past_year_start()
        
        # Prepare result with past year count
        result = []
        for artist, total_count in top_artists:
            # Count listens from past year
            past_year_count = sum(
                1 for listen in listen_history
                if listen["artist"] == artist and 
                datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > past_year_start
            )
            
            result.append({
                "name": artist,
                "total_count": total_count,
                "past_year_count": past_year_count
            })
            
        return result
    
    @staticmethod
    def get_album_stats(listen_history, limit):
        """Generate album statistics with past year count"""
        # First identify albums with multiple artists
        album_artists = {}
        for listen in listen_history:
            album = listen["album"]
            artist = listen["artist"]
            if album not in album_artists:
                album_artists[album] = set()
            album_artists[album].add(artist)
        
        # Create a new counter for albums, handling various artists
        album_play_counter = {}
        for listen in listen_history:
            album = listen["album"]
            if len(album_artists[album]) > 1:
                # Multiple artists - count as "Various Artists"
                key = (album, "Various Artists")
            else:
                # Single artist
                key = (album, listen["artist"])
            
            album_play_counter[key] = album_play_counter.get(key, 0) + 1
        
        # Convert to counter for most_common
        album_counter = Counter(album_play_counter)
        top_albums = album_counter.most_common(limit)
        
        # Get past year start date
        past_year_start = ListenAnalyser.get_past_year_start()
        
        # Prepare result with past year count
        result = []
        for (album, artist), total_count in top_albums:
            # For past year count, need to consider if it's a various artists album
            if artist == "Various Artists":
                # Count past year plays for this album, any artist
                past_year_count = sum(
                    1 for listen in listen_history
                    if listen["album"] == album and
                    datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > past_year_start
                )
            else:
                # Count past year plays for this specific album+artist
                past_year_count = sum(
                    1 for listen in listen_history
                    if listen["album"] == album and listen["artist"] == artist and
                    datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > past_year_start
                )
            
            is_various = artist == "Various Artists"
            result.append({
                "name": album,
                "artist": artist,
                "is_various_artists": is_various,
                "total_count": total_count,
                "past_year_count": past_year_count
            })
        
        return result
    
    @staticmethod
    def get_song_stats(listen_history, limit):
        """Generate song statistics with past year count"""
        # Count by song+artist combination
        song_counter = Counter([(listen["song"], listen["artist"]) for listen in listen_history])
        top_songs = song_counter.most_common(limit)
        
        # Get past year start date
        past_year_start = ListenAnalyser.get_past_year_start()
        
        # Prepare result with past year count
        result = []
        for (song, artist), total_count in top_songs:
            # Count listens from past year
            past_year_count = sum(
                1 for listen in listen_history
                if listen["song"] == song and listen["artist"] == artist and
                datetime.strptime(listen["datetime"], "%Y-%m-%d %H:%M:%S") > past_year_start
            )
            
            result.append({
                "name": song,
                "artist": artist,
                "total_count": total_count,
                "past_year_count": past_year_count
            })
            
        return result
    
    @staticmethod
    def get_stats_for_timeframe(listen_history, field_type, timeframe):
        """Get stats for a specific field and timeframe with appropriate count limit"""
        filtered_history = ListenAnalyser.filter_by_timeframe(listen_history, timeframe)
        limit = WEEKLY_TOP_COUNT if timeframe == TimeFrame.LAST_WEEK else ALL_TIME_TOP_COUNT
        
        if field_type == ListenField.ARTIST:
            return ListenAnalyser.get_artist_stats(filtered_history, limit)
        elif field_type == ListenField.ALBUM:
            return ListenAnalyser.get_album_stats(filtered_history, limit)
        elif field_type == ListenField.SONG:
            return ListenAnalyser.get_song_stats(filtered_history, limit)

class SpotifyDigest:
    """Main class for generating Spotify digest emails"""
    
    def __init__(self):
        self.analyser = ListenAnalyser()
        self.listen_history = self.analyser.get_listen_history()
        self.past_year_start = self.analyser.get_past_year_start()
        print(f"Analysing data including past year (since {self.past_year_start.strftime('%d %b %Y')})")
    
    def get_email_subject(self, top_artists):
        """Generate email subject based on top artists"""
        if len(top_artists) >= 3:
            return f"Your Spotify weekly digest - featuring {top_artists[0]['name']}, {top_artists[1]['name']} and {top_artists[2]['name']}"
        elif len(top_artists) == 2:
            return f"Your Spotify weekly digest - featuring {top_artists[0]['name']} and {top_artists[1]['name']}"
        elif len(top_artists) == 1:
            return f"Your Spotify weekly digest - featuring {top_artists[0]['name']}"
        else:
            return "Your Spotify weekly digest"
    
    def get_data(self):
        """Prepare all data needed for the email template"""
        data = {
            "past_year_start": self.past_year_start.strftime("%d %b %Y"),
            "weekly_count": WEEKLY_TOP_COUNT,
            "all_time_count": ALL_TIME_TOP_COUNT,
            "fields": {}
        }
        
        # Process each field type (artist, album, song)
        for field in ListenField:
            field_data = {}
            
            # Process each timeframe (last week, all time)
            for timeframe in TimeFrame:
                # Generate stats for this field and timeframe
                stats = self.analyser.get_stats_for_timeframe(
                    self.listen_history, field, timeframe
                )
                field_data[timeframe.value] = stats
            
            data["fields"][field.value] = field_data
        
        return data
    
    def get_html_content(self, data):
        """Generate HTML email content"""
        environment = jj2.Environment(loader=jj2.FileSystemLoader(dirname(abspath(__file__))))
        template = environment.get_template("email_template.html")
        return template.render(**data)
    
    def get_text_content(self, data):
        """Generate plain text email content"""
        text_sections = []
        
        for field_name, field_data in data["fields"].items():
            for timeframe, items in field_data.items():
                count = WEEKLY_TOP_COUNT if timeframe == "the past seven days" else ALL_TIME_TOP_COUNT
                section = f"Your top {count} {field_name}s of {timeframe} are:"
                
                for i, item in enumerate(items, 1):
                    if field_name == "artist":
                        line = f"{i}. {item['name']}: {item['total_count']} plays"
                    else:
                        line = f"{i}. {item['name']} by {item['artist']}: {item['total_count']} plays"
                    
                    # For all-time, add past year count
                    if timeframe == "all time" and item['past_year_count'] > 0:
                        line += f" ({item['past_year_count']} in past year)"
                    
                    section += f"\n{line}"
                
                text_sections.append(section)
        
        return "\n\n".join(text_sections)
    
    def generate_email(self):
        """Generate complete email with subject, HTML, and text content"""
        data = self.get_data()
        last_week_artists = data["fields"]["artist"]["the past seven days"]
        
        return {
            "subject": self.get_email_subject(last_week_artists),
            "html_content": self.get_html_content(data),
            "text_content": self.get_text_content(data)
        }
    
    def send_email(self, email_data):
        """Send email using local SMTP server"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = email_data["subject"]
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        part1 = MIMEText(email_data["text_content"], "plain")
        part2 = MIMEText(email_data["html_content"], "html")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP("localhost") as server:
            server.sendmail(EMAIL, [EMAIL], msg.as_string())
        print("Email sent successfully.")

    def preview(self):
        """Generate preview HTML file"""
        email_data = self.generate_email()
        with open("email.html", "w", encoding="utf-8") as f:
            f.write(email_data["html_content"])
        print("Preview written to email.html.")

def main():
    digest = SpotifyDigest()
    email_data = digest.generate_email()
    digest.send_email(email_data)

if __name__ == "__main__":
    main()