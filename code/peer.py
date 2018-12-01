from flask import Flask, request, jsonify
from argparse import ArgumentParser, ArgumentTypeError
from threading import Thread
import http.client as httplib
from broadcastSys import failureDetector
import json
import time

class Peer:
    def __init__(self, bootsDist, bootsLoc):
        self.serverSide = Server(bootsLoc, self)
        self.clientSide = Client(bootsDist, bootsLoc, self)
        pass

    def removeConnection(self):
        self.clientSide.disconnect()

class Server:
    def __init__(self, address, peer):
        self.peer = peer
        self.server = Thread(target = self.launchServer, args=[address])
        self.server.start()
        pass

    def launchServer(self, args):

        address = args
        self.app = Flask(__name__)
        self.app.add_url_rule('/addNode/', 'addNode', self.addNode, methods = ['POST'])
        self.app.add_url_rule('/rmNode/', 'rmNode', self.rmNode, methods = ['POST'])

        self.failDetect= failureDetector("{}:{}".format(host, port), ["{}:{}".format(host, port)], 15, self.app)

        myList = address.split(':')
        host = myList[0]
        port = myList[1]
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def addNode(self):
        node = request.get_json()
        self.failDetect.addNode(node)

        return json.dumps("Nood succefuly added to ___")

    def rmNode(self):
        node = request.get_json()
        self.failDetect.rmNode(node)
        return "node removed"

class Client:
    def __init__(self, bootsDist, bootsLoc, peer):
        self.bootsDist = bootsDist
        self.bootsLoc = bootsLoc
        self.peer = peer
        self.contactDistBoost()
        self.connectToNodes()

    def broadcast(self, method, url, jsonObj, headers):

        for connected in self.peer.serverSide.failDetect.alive:
            if connected != self.bootsLoc:
                conn = httplib.HTTPConnection("{}".format(connected))
                conn.request(method, url, jsonObj)

    def contactDistBoost(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("POST","/joinP2P", json.dumps(self.bootsLoc),{'content-type': 'application/json'})
        response = conn.getresponse().read()
        self.peer.serverSide.failDetect.alive = json.loads(response)


    def connectToNodes(self):
        self.broadcast("POST","/addNode", json.dumps(self.bootsLoc), {'content-type': 'application/json'})

    def disconnect(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("DELETE","/rmNode", json.dumps(self.bootsLoc), {'content-type': 'application/json'})

        #TODO: broadcast disconnect to every node
        self.broadcast('DELETE', "/rmNode", json.dumps(self.bootsLoc), {'content-type': 'application/json'})

def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--bootsloc',
        default="8001")
    args = parser.parse_args()

    bootsDist = "192.168.1.60:8000"
    bootsLoc = "192.168.1.60:{}".format(args.bootsloc)
    peer = Peer(bootsDist, bootsLoc)

    input()
    print(peer.serverSide.failDetect.alive)
    input()
    peer.removeConnection()

    return 0

if __name__ == "__main__":
    main()
