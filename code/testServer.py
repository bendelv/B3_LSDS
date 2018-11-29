from flask import Flask, request
import http.client as httplib
from threading import Thread
import time

app = Flask(__name__)


class simpletP2P(object):
    def __init__(self, host, port):
        server = Thread(target = launchServer, args = (host, port))
        server.start()
        time.sleep(2)
        conn = httplib.HTTPConnection("{}:{}".format(host, port))
        conn.request("GET","/connectedUsers")
        res = conn.getresponse()
        print(res.read())
        conn.request("GET","/niqueTaMereBen")
        res = conn.getresponse()
        print(res.read())

    @app.route('/connectedUsers')
    def index():
        return 'Hello world'

    def coucou():
        return 'coucou'

    @app.route('/niqueTaMereBen')
    def YES():
        return 'bien joue'


def launchServer(host, port):
    app.run(debug=True, use_reloader=False, host=host, port=port)


def main():
    sp = simpletP2P("0.0.0.0", "8080")

if __name__ == '__main__':
    main()
