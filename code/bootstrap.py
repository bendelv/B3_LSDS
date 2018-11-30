from flask import Flask, request
from threading import Thread
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
        self.app.add_url_rule('/addNode/', 'add_node', self.add_node, methods=['GET', 'POST'])
        self.app.add_url_rule('/rmNode/', 'rm_node', self.remove_node, methods=['DELETE'])
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def home_page(self):
        return "<b> Current nodes = {} </b>".format(self.nodes)

    def add_node(self):
        address = request.args.get('address', '')
        self.returnAddress = address
        # optimization, implement nodes as a dict for a lookup in O(1) instead
        # of O(n), OKAY here as we assume a small amount of nodes
        if address not in self.nodes:
            self.nodes.append(address)
            print(self.nodes)

        return json.dumps(self.nodes)

    def remove_node(self):
        address = request.args.get('address', '')
        if address in self.nodes:
            self.nodes.remove(address)
            print(self.nodes)
        return "node removed"

    def send_nodes(self):
        conn = httplib.HTTPConnection(self.address)
        conn.request("POST", '/receiveAddressList/?addresses={}'.format(json.dumps(selef.nodes)))
        res = conn.getresponse()
        print(res.read())

def main():
    b = Bootstrap("192.168.1.50","8000")

if __name__ == "__main__":
    main()
