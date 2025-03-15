import os
import json
from Spotify import Spotify

# Use the same local file path for play history; ensure that this volume is shared with listen_summary.
PLAY_HISTORY_FILE = os.environ.get("PLAY_HISTORY_FILE", "/data/spotify-play-history.json")
spotify = Spotify()

def load_listen_history():
    if os.path.exists(PLAY_HISTORY_FILE):
        with open(PLAY_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def put_listen_history(listen_history):
    with open(PLAY_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(listen_history, f, indent=2)
    print(f"Listen history successfully written to {PLAY_HISTORY_FILE}")

def update_listen_history(listen_history, recent_listens):
    listen_history_ids = {x["listen_id"] for x in listen_history}
    listens_added = 0
    for recent_listen in reversed(recent_listens):
        if recent_listen["listen_id"] not in listen_history_ids:
            listen_history.append(recent_listen)
            listens_added += 1
    put_listen_history(listen_history)
    print(f"{listens_added} new listens added!")
    print("Total number of listens logged: " + str(len(listen_history)))

def main():
    recent_listens = spotify.get_recent_listens()
    try:
        print("Getting listen history from local file...")
        listen_history = load_listen_history()
        print("Updating listen history...")
        update_listen_history(listen_history, recent_listens)
    except Exception as e:
        print("Error accessing local listen history file, creating new file...")
        put_listen_history(recent_listens)

if __name__ == "__main__":
    main()
