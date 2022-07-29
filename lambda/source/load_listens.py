import mysql.connector as mysql
import os

from Spotify import Spotify

def handler(event, context):
    print('Connecting to database...')
    cnx = mysql.connect(
        user     = os.environ.get('DB_USER'),
        password = os.environ.get('DB_PASSWORD'),
        host     = os.environ.get('DB_HOST'),
        port     = int(os.environ.get('DB_PORT'))
    )
    create_database = "CREATE DATABASE IF NOT EXISTS spotify"
    use_database = "USE spotify"
    create_table = (
        "CREATE TABLE IF NOT EXISTS spotify ("
            "`datetime` DATETIME,"
            "artist VARCHAR(250),"
            "album VARCHAR(250),"
            "song VARCHAR(250)"
        ")"
    )
    add_play = (
        "INSERT INTO spotify.spotify (`datetime`, artist, album, song)"
        "VALUES"
        "(%(datetime)s, %(artist)s, %(album)s, %(song)s)"
    )
    cursor = cnx.cursor()
    print("Creating Spotify database if not exists...")
    cursor.execute(create_database)
    print("Switching to Spotify database...")
    cursor.execute(use_database)
    print("Creating Spotify table if not exists...")
    cursor.execute(create_table)
    cnx.commit()
    spotify = Spotify()
    play_history = spotify.get_play_history()
    i = 0
    for play in play_history:
        try:
            print("Storing play number " + str(i + 1))
            cursor.execute(add_play, play)
            cnx.commit()
            i += 1
        except:
            pass
    cursor.close()
    cnx.close()
    print(f'{i} plays added!')