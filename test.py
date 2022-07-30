import json

# from Spotify import Spotify

# spotify = Spotify()
# recent_listens = spotify.get_recent_listens()
# print(json.dumps(recent_listens))

with open('listen_history.json') as f:
    listen_history = f.read()

with open('recent_listens.json') as f:
    recent_listens = f.read()

listen_history = json.loads(listen_history)
recent_listens = json.loads(recent_listens)
listen_history_listen_ids = [x['listen_id'] for x in listen_history]
for recent_listen in recent_listens:
    if recent_listen['listen_id'] not in listen_history_listen_ids:
        listen_history.insert(0, recent_listen)
a = 1