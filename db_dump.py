from dotenv import load_dotenv
import mysql.connector
import os

from main import GetData

command = "net start mysql80"
os.system(command)

print('Loading last 50 Spotify plays into local MySQL database...')

load_dotenv()

cnx = mysql.connector.connect(
    user     = os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host     = os.environ.get('DB_HOST'),
    port     = os.environ.get('DB_PORT')
)

add_play = (
"INSERT INTO spotify.spotify (`datetime`, artist, album, song)"
"VALUES"
"(%(datetime)s, %(artist)s, %(album)s, %(song)s)"
)

cursor = cnx.cursor()

a = GetData()
play_history = a.get_play_history()
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

command = "net stop mysql80"

os.system(command)
# else:
#     # Re-run the program with admin rights
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)