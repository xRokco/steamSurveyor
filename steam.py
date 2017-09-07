import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import sys
import sqlite3
from datetime import datetime

conn = sqlite3.connect('steam.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS games (time text, game text)")
c.execute("CREATE TABLE IF NOT EXISTS gamelist (game text, UNIQUE(game))")

url = 'http://steamcommunity.com/id/Rokco'

req = urllib.request.Request(url)

try:
    response = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    sys.exit(str(e))

html = response.read()

parsed_html = BeautifulSoup(html, "html.parser")

date = str(datetime.now())
try:
    game = parsed_html.body.find('div', attrs={'class':'profile_in_game_name'}).text
    if game.startswith('Last Online'):
        #offline
        game = "offline"
except AttributeError:
    #online, no game
    game = "online"

c.execute("INSERT INTO games VALUES ('"+date+"','"+game+"')")
c.execute("INSERT OR IGNORE INTO gamelist VALUES ('"+game+"')")

conn.commit()
conn.close()