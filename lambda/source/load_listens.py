import mysql.connector as mysql
import os

from Spotify import Spotify

def handler(event, context):
    print('Loading last 50 Spotify plays into MySQL database...')
    print('OS environ:\n', os.environ)
    cnx = mysql.connect(
        user     = os.environ.get('DB_USER'),
        password = os.environ.get('DB_PASSWORD'),
        host     = os.environ.get('DB_HOST'),
        port     = int(os.environ.get('DB_PORT'))
    )
    add_play = (
        "INSERT INTO spotify.spotify (`datetime`, artist, album, song)"
        "VALUES"
        "(%(datetime)s, %(artist)s, %(album)s, %(song)s)"
    )
    cursor = cnx.cursor()
    spotify = Spotify()
    play_history = spotify.get_play_history()
    i = 0
    for play in play_history:
        try:
            cursor.execute(add_play, play)
            cnx.commit()
            i += 1
        except:
            pass
    cursor.close()
    cnx.close()
    print(f'{i} plays added!')