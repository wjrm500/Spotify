from secrets import refresh_token, base64
import requests

class Refresh():
    def __init__(self):
        self.refresh_token = refresh_token
        self.base64 = base64

    def refresh(self):
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(query,
            data = {"grant_type": "refresh_token",
                    "refresh_token": refresh_token},
            headers = {"Authorization": "Basic {}".format(base64)}
            )
        response_json = response.json()
        return response_json["access_token"]