from dotenv import load_dotenv
import mysql.connector as mysql
import os

load_dotenv()

cnx = mysql.connect(
    user     = os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host     = os.environ.get('DB_HOST'),
    port     = int(os.environ.get('DB_PORT'))
)
sql = "SELECT * FROM spotify.spotify"
cursor = cnx.cursor()
cursor.execute(sql)
result = cursor.fetchall()
a = 1 # Test