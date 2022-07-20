import package.requests as requests

from secrets import *
from refresh import *

class Spotify:
    def __init__(self):
        self.user_id = spotify_user_id
        refreshCaller = Refresh()
        self.spotify_token = refreshCaller.refresh()

    def get_playlist(self, playlist_type):
        if playlist_type == "dw":
            self.playlist_id = discover_weekly_id
            print("Finding songs in Discover Weekly...")
        elif playlist_type == "fs":
            self.playlist_id = favourite_songs_id
            print("Finding songs in Favourite Songs...")
        playlist = []
        offset = 0
        keep_going = True
        while keep_going:
            query = "https://api.spotify.com/v1/playlists/{}/tracks?offset={}".format(self.playlist_id, offset)
            response = requests.get(query,
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.spotify_token)
                    }
                )
            response_json = response.json()
            keep_going = True if len(response_json["items"]) == 100 else False
            for j in response_json["items"]:
                try:
                    artist = j["track"]["album"]["artists"][0]["name"]
                    album = j["track"]["album"]["name"]
                    song = j["track"]["name"]
                    playlist.append({
                        "artist": artist,
                        "album": album,
                        "song": song
                    })
                except:
                    pass
            offset += 100
        print(playlist)
        print(len(playlist))

    def get_play_history(self):
        query = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
        response = requests.get(query,
            headers = {
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        play_history = []
        for j in response_json["items"]:
            try:
                datetime = j["played_at"]
                a = datetime[0:10]
                b = datetime[11:19]
                datetime = a + " " + b
                artist = j["track"]["album"]["artists"][0]["name"]
                album = j["track"]["album"]["name"]
                song = j["track"]["name"]
                play_history.append({
                    "datetime": datetime,
                    "artist": artist,
                    "album": album,
                    "song": song
                })
            except:
                pass
        return play_history