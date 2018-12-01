from flask import Flask, request
from threading import Thread
from broadcastSys import failureDetector
import http.client as httplib
import json
import time

class Bootstrap(object):
    def __init__(self, host, port):
        self.nodes = []
        server = Thread(target = self.launchServer, args = (host, port))
        server.start()


    def launchServer(self, host, port):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home_page, methods=['GET'])
        self.app.add_url_rule('/joinP2P', 'join_P2P', self.joinP2P, methods=['POST'])
        self.app.add_url_rule('/rmNode', 'rm_node', self.rmNode, methods=['DELETE'])

        self.failDetect= failureDetector("{}:{}".format(host, port), ["{}:{}".format(host, port)], 15, self.app)
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def home_page(self):
        return "<b> Current nodes = {} </b>".format(self.nodes)

    def getConnectedPeers(self):
        return self.failDetect.alive

    def joinP2P(self):
        node = request.get_json()
        self.failDetect.addNode(node)
        return json.dumps(self.getConnectedPeers())

    def rmNode(self):
        node = request.get_json()
        self.failDetect.rmNode(node)
        return "node removed"

    def send_nodes(self):
        conn = httplib.HTTPConnection(self.address)
        conn.request("POST", '/receiveAddressList/?addresses={}'.format(json.dumps(selef.nodes)))
        res = conn.getresponse()
        print(res.read())

def main():
    b = Bootstrap("192.168.1.60","8000")

if __name__ == "__main__":
    main()
