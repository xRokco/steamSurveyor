import string
import sqlite3
import cherrypy
import json
import os, os.path
import time

import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import sys
from datetime import datetime
from cherrypy.process.plugins import BackgroundTask

class StringGenerator(object):
    @cherrypy.expose
    def data(self):
        conn = sqlite3.connect('public/steam.db')
        c = conn.cursor()
        c.execute("SELECT * FROM games")
        json_string = json.dumps(c.fetchall())
        c.execute("SELECT * FROM gamelist")
        json_string += "###"+json.dumps(c.fetchall())
        return json_string

    @cherrypy.expose
    def index(self):
        return open("chart.html")

    def _task(self):
        conn = sqlite3.connect('public/steam.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS games (time text, game text)")

        url = 'http://steamcommunity.com/id/Rokco'

        req = urllib.request.Request(url)

        print("updating")
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

        conn.commit()

        conn.close()

if __name__ == '__main__':
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 80
    if len(sys.argv) > 1:
        cherrypy.server.socket_port = int(sys.argv[1])
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    StringGenerator()._task()
    BackgroundTask(59, StringGenerator()._task, bus = cherrypy.engine).start()
    cherrypy.quickstart(StringGenerator(), '/', conf)