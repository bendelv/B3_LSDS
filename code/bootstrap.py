from flask import Flask, request
from threading import Thread
import http.client as httplib
import json
import time

from broadcastSys import PerfecFailureDetector
from broadcastSys import PerfectLink

class Bootstrap(object):
    def __init__(self, host, port):
        self.bootsLoc = "{}:{}".format(host, port)
        self.pl = PerfectLink()
        self.server = Thread(target = self.launchServer, args = (host, port))
        failDetect = PerfecFailureDetector(["{}:{}".format(host, port)], 5, self)
        server.start()

    def launchServer(self, host, port):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home_page, methods=['GET'])
        self.app.add_url_rule('/joinP2P', 'join_P2P', self.joinP2P, methods=['POST'])
        self.app.add_url_rule('/rmNode', 'rm_node', self.rmNode, methods=['DELETE'])

        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def home_page(self):
        return "<b> Current nodes = {} </b>".format(self.failDetect.get_alive())



    def rmNode(self):
        node = request.get_json()
        self.failDetect.rm_node(node)
        return "node removed"

def main():
    b = Bootstrap("10.9.172.251","8000")

if __name__ == "__main__":
    main()
