from flask import Flask, request, jsonify
from argparse import ArgumentParser, ArgumentTypeError
from threading import Thread
import http.client as httplib
import numpy as np
import socket
import json
import time


import blockchain
from broadcastSys import ReliableBroadcast
from broadcastSys import PerfecFailureDetector
from broadcastSys import PerfectLink

class Peer:
    def __init__(self, blockchain, bootsDist, bootsLoc):
        self._blockchain = blockchain
        self.bootsLoc = bootsLoc
        self.bootsDist = bootsDist

        self.serverSide = Server(bootsLoc, self)
        time.sleep(1)
        self.pl = PerfectLink()
        self.pfd = PerfecFailureDetector(["{}".format(bootsLoc)], 5, self)
        self.rb = ReliableBroadcast("{}".format(bootsLoc), self)
        time.sleep(2)
        self.clientSide = Client(bootsDist, bootsLoc, self)
        pass

    def removeConnection(self):
        self.serverSide.disconnect()
        self.clientSide.disconnect()

    def broadcastFoundBlock(self, block):
        self.clientSide.broadcastFoundBlock(block)

    def broadcastTransaction(self, transaction):
        self.client.broadcastTransaction()

class Server:
    def __init__(self, address, peer):
        self.peer = peer
        self.server = Thread(target = self.launchServer, args=[address])
        self.server.start()

    def launchServer(self, args):

        address = args
        self.app = Flask(__name__)
        self.app.add_url_rule('/joinP2P', 'join_P2P', self.joinP2P, methods=['POST'])
        self.app.add_url_rule('/rb/addNode', 'addNode', self.addNode, methods = ['POST'])
        self.app.add_url_rule('/rb/rmNode', 'rmNode', self.rmNode, methods = ['DELETE'])
        self.app.add_url_rule('/rb/addTransaction', 'addTransaction', self.addTransaction, methods = ['POST'])
        self.app.add_url_rule('/rb/blockMined', 'blockMined', self.blockMined, methods = ['POST'])
        self.app.add_url_rule('/askBC', 'askBC', self.askBC, methods = ['GET'])
        self.app.add_url_rule('/view', 'view', self.view, methods = ['GET'])

        myList = address.split(':')
        host = myList[0]
        port = myList[1]
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def joinP2P(self):
        objNode = request.get_json()
        self.peer.pfd.add_node(objNode[0])
        list = self.peer.pfd.get_alive()
        return json.dumps(list)

    def addNode(self):
        objNode = request.get_json()
        self.peer.pfd.add_node(objNode[0]['msg'])
        self.peer.rb.rbHandler(objNode[1], 'POST', '/rb/addNode', objNode[0])

        if self.peer._blockchain.length() > 1:
            return json.dumps([self.peer._blockchain.getHash(),
                               self.peer._blockchain.getTransactions()],
                                default=lambda o: o.__dict__, indent=4)

        return json.dumps([None, self.peer._blockchain.getTransactions()],
                          default=lambda o: o.__dict__, indent=4)

    def rmNode(self):
        objNode = request.get_json()
        self.peer.rb.rbHandler(objNode[1], 'DELETE', '/rb/rmNode', objNode[0])
        self.peer.pfd.rm_node(objNode[0]['msg'])
        return json.dumps('')
    #To be tested when broadcast available
    def addTransaction(self):
        transaction = request.get_json()
        transaction = blockchain.Transaction.fromJsonDict(json.loads(transaction))
        peer._blockchain.loc_add_transaction(transaction)

    def blockMined(self):
        block = request.get_json()
        rb.hander(method, url, block)
        self._blockchain.set_blockReceived(block)
        pass

    def askBC(self):
        return self.peer._blockchain.toJson2()

    def view(self):
        title = "<h1> log page Blockchain</h1>"
        return title + self.peer._blockchain.toHtml()

    def disconnect(self):
        #self.app.terminate()
        self.app.join()

class Client:
    def __init__(self, bootsDist, bootsLoc, peer):
        self.bootsDist = bootsDist
        self.bootsLoc = bootsLoc
        self.peer = peer
        self.contactDistBoost()
        self.connectToNodes()

    def contactDistBoost(self):
        objNodes = self.peer.pl.send(self.bootsLoc, self.bootsDist, "POST", "/joinP2P", self.bootsLoc)
        self.peer.pfd.add_nodes(objNodes)

    def connectToNodes(self):
        res = self.peer.rb.broadcast("POST","/rb/addNode", self.bootsLoc)
        hashes = np.array([x[0][0] for x in res],dtype=object)
        processes = np.array([x[1] for x in res],dtype=object)
        all_transactions = np.array([x[0][1] for x in res],dtype=object)
        for transactions in all_transactions:
            for transaction in transactions:
                t = blockchain.Transaction.fromJsonDict(transaction)
                self.peer._blockchain.addTransaction(t, False)

        # No block in the chain for now
        hashes[np.where(hashes == None)] = ''
        unique, counts = np.unique(hashes, return_counts=True)
        best_hash = unique[np.argmax(counts)]
        if best_hash == '':
            return

        best_process = processes[np.where(hashes == best_hash)]

        blocks = self.peer.pl.send(best_process, "GET", "/askBC", '')
        self.peer._blockchain.setStorage(blocks)

    def broadcastTransaction(self):
        #TODO when broadcast available
        pass

    def broadcastFoundBlock(self, block):

        pass

    def disconnect(self):
        objH = self.peer.rb.broadcast("DELETE", "/rb/rmNode", self.bootsLoc)


def main(args):

    bootsDist = "10.9.172.251:8000"
    bootsLoc = "10.9.172.251:{}".format(args.bootsloc)
    peer = Peer(bootsDist, bootsLoc)

    return 0

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '--bootsloc',
        default="8001")
    args = parser.parse_args()
    main(args)
