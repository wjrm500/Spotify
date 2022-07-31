from collections import Counter
from datetime import datetime, timedelta
import json

with open('listen_history.json') as f:
    listen_history = f.read()

listen_history = json.loads(listen_history)
one_week_ago = datetime.now() - timedelta(days = 7)
last_week_listens = [x for x in listen_history if datetime.strptime(x['datetime'], '%Y-%m-%d %H:%M:%S') > one_week_ago]
artist_plays = Counter([x['artist'] for x in last_week_listens])
top_artists = artist_plays.most_common(5)
email_content = 'Your most played artists over the past week are:\n' + '\n'.join(x[0] + ': ' + str(x[1]) for x in top_artists)