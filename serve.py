import string
import sqlite3
import cherrypy
import json
import os, os.path
import time
import requests
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

        url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=58DD6DFA4A77663D10F94D79E7AC6F4F&steamids=76561198024504284'

        resp = requests.get(url=url)
        data = json.loads(resp.text)

        print("updating")

        date = str(datetime.now())
        try:
            # in game
            game = resp.json()['response']['players'][0]['gameextrainfo']
        except KeyError:
            #not in game
            if resp.json()['response']['players'][0]['personastate'] == 0 or resp.json()['response']['players'][0]['personastate'] == 2 or resp.json()['response']['players'][0]['personastate'] == 3 or resp.json()['response']['players'][0]['personastate'] == 4:
                game = "Offline"
            elif resp.json()['response']['players'][0]['personastate'] == 1 or resp.json()['response']['players'][0]['personastate'] == 5 or resp.json()['response']['players'][0]['personastate'] == 6:
                game = "Online"       

        c.execute("UPDATE games set game = REPLACE('Away','Away','Offline')")
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