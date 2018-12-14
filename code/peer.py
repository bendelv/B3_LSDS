from flask import Flask, request, jsonify
from argparse import ArgumentParser, ArgumentTypeError
from threading import Thread
import http.client as httplib

import socket
import json
import time

from broadcastSys import FailureDetector
from application import Transaction

class Peer:
    def __init__(self, blockchain, bootsDist, bootsLoc):
        self._blockchain = blockchain
        self.serverSide = Server(bootsLoc, self)
        time.sleep(1)
        self.clientSide = Client(bootsDist, bootsLoc, self)
        self.pfd = FailureDetector("{}".format(bootsLoc), ["{}".format(bootsLoc)], 5, self.serverSide.app)
        self.rb = ReliableBroadcast("{}".format(bootsLoc),  ["{}".format(bootsLoc)], self.serverSide.app, None, self.pfd)
        pass

    def removeConnection(self):
        self.clientSide.disconnect()

    def broadcast_foundBlock(self, block):
        self.clientSide.broadcast_foundBlock(block)

class Server:
    def __init__(self, address, peer):
        self.peer = peer
        self.server = Thread(target = self.launchServer, args=[address])
        self.server.start()

    def launchServer(self, args):

        address = args
        self.app = Flask(__name__)
        self.app.add_url_rule('/rb/addNode', 'addNode', self.addNode, methods = ['POST'])
        self.app.add_url_rule('/rb/rmNode', 'rmNode', self.rmNode, methods = ['POST'])
        self.app.add_url_rule('/rb/addTransaction', 'addTransaction', self.addTransaction, methods = ['POST'])
        self.app.add_url_rule('/rb/blockMined', 'blockMined', self.blockMined, methods = ['POST'])


        myList = address.split(':')
        host = myList[0]
        port = myList[1]
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def addNode(self):
        node = request.get_json()
        self.peer.rb.rbHandler('POST', '/rb/addNode', node)
        self.peer.pfd.add_node(node)
        return json.dumps("Nood succefuly added to ___")

    def rmNode(self):
        node = request.get_json()
        self.perr.pfd.rm_node(node)
        return "node removed"

    #To be tested when broadcast available
    def addTransaction(self):
        transaction = request.get_json()
        transaction = Transaction.fromJsonDict(json.loads(transaction))
        peer._blockchain.loc_add_transaction(transaction)

    def blockMined(self):
        block = request.get_json()
        rb.hander(method, url, block)
        self._blockchain.set_blockReceived(block)
        pass

class Client:
    def __init__(self, bootsDist, bootsLoc, peer):
        self.bootsDist = bootsDist
        self.bootsLoc = bootsLoc
        self.peer = peer
        self.contactDistBoost()
        self.connectToNodes()

    def broadcast(self, method, url, jsonObj, headers):

        for connected in self.peer.pfd.alive:
            if connected != self.bootsLoc:
                conn = httplib.HTTPConnection("{}".format(connected))
                conn.request(method, url, jsonObj)

    def contactDistBoost(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("POST","/joinP2P", json.dumps(self.bootsLoc),{'content-type': 'application/json'})
        response = conn.getresponse().read()
        print(response.decode())
        self.peer.pfd.alive = json.loads(response.decode())


    def connectToNodes(self):
        self.broadcast("POST","/addNode", json.dumps(self.bootsLoc), {'content-type': 'application/json'})

    def broadcastTransaction():
        #TODO when broadcast available
        pass

    def broadcast_foundBlock(self, block):

        pass

    def disconnect(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("DELETE","/rmNode", json.dumps(self.bootsLoc), {'content-type': 'application/json'})

        self.broadcast('DELETE', "/rmNode", json.dumps(self.bootsLoc), {'content-type': 'application/json'})

def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--bootsloc',
        default="8001")
    args = parser.parse_args()

    bootsDist = "192.168.1.25:8000"
    bootsLoc = "192.168.1.60:{}".format(args.bootsloc)
    peer = Peer(bootsDist, bootsLoc)

    input()
    print(peer.pfd.alive)
    input()
    peer.removeConnection()

    return 0

if __name__ == "__main__":
    main()
