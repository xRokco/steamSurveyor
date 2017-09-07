import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import sys
import sqlite3
from datetime import datetime

conn = sqlite3.connect('steam.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS games (time text, game text)''')

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
		c.execute("INSERT INTO games VALUES ('"+date+"','offline')")
	else:
		#online, in game
		c.execute("INSERT INTO games VALUES ('"+date+"','"+game+"')")
except AttributeError:
	#online, no game
	game = parsed_html.body.find('div', attrs={'class':'profile_in_game_name'}).text
	c.execute("INSERT INTO games VALUES ('"+date+"','online')")

conn.commit()
conn.close()