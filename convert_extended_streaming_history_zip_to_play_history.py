import os
import json
import zipfile
import hashlib
from tqdm import tqdm
from datetime import datetime

def extract_zip(zip_path, extract_to):
    """Extracts the Spotify data zip file."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def get_audio_files(folder):
    """Gets all audio streaming history JSON files."""
    return sorted(
        [f for f in os.listdir(folder) if f.startswith("Streaming_History_Audio") and f.endswith(".json")]
    )

def generate_listen_id(entry):
    """Generates a unique listen ID using a hash of relevant fields."""
    data = f"{entry['ts']}{entry['master_metadata_track_name']}{entry['master_metadata_album_artist_name']}{entry['master_metadata_album_album_name']}"
    return hashlib.md5(data.encode()).hexdigest()

def parse_streaming_history(folder):
    """Parses all audio streaming history JSON files and returns a sorted list of listens."""
    listens = []
    audio_files = get_audio_files(folder)
    
    for file in tqdm(audio_files, desc="Processing Files", unit="file"):
        with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            for entry in tqdm(data, desc=f"Reading {file}", unit="entry", leave=False):
                if entry.get("master_metadata_track_name") and entry.get("master_metadata_album_artist_name"):
                    listens.append({
                        "listen_id": generate_listen_id(entry),
                        "datetime": datetime.strptime(entry["ts"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S"),
                        "artist": entry["master_metadata_album_artist_name"],
                        "album": entry["master_metadata_album_album_name"],
                        "song": entry["master_metadata_track_name"]
                    })
    
    # Sort listens chronologically
    listens.sort(key=lambda x: x["datetime"])
    return listens

def write_to_json(data, output_file):
    """Writes parsed listen data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    zip_path = "my_spotify_data.zip"
    extract_to = "spotify_data"
    output_file = "spotify-play-history.json"
    
    print("Extracting zip file...")
    extract_zip(zip_path, extract_to)
    
    folder = os.path.join(extract_to, "Spotify Extended Streaming History")
    print("Processing streaming history...")
    listens = parse_streaming_history(folder)
    
    print("Writing to output file...")
    write_to_json(listens, output_file)
    print(f"Done! Data written to {output_file}")

if __name__ == "__main__":
    main()
