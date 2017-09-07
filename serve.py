import string
import sqlite3
import cherrypy
import json


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        conn = sqlite3.connect('steam.db')
        c = conn.cursor()
        c.execute("SELECT * FROM games")
        json_string = json.dumps(c.fetchall())
        return json_string

    @cherrypy.expose
    def chart(self):
        return open("chart.html")

if __name__ == '__main__':
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 80
    cherrypy.quickstart(StringGenerator())