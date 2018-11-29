from flask import Flask, request
import http.client as httplib
from threading import Thread
import time


class simpletP2P(object):

    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'coucou', self.coucou)
        server = Thread(target = self.launchServer, args = (host, port))
        server.start()
        time.sleep(2)

    def coucou(self):
        return "coucou"


    def launchServer(self, host, port):
        self.app.run(debug=True, use_reloader=False, host=host, port=port)


def main():
    sp = simpletP2P("0.0.0.0", "8080")

if __name__ == '__main__':
    main()
