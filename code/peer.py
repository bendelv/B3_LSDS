from flask import Flask, request, jsonify
from argparse import ArgumentParser, ArgumentTypeError
from threading import Thread
import http.client as httplib
import numpy as np
import socket
import json
import time


from application import Transaction
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
        time.sleep(1)
        self.clientSide = Client(bootsDist, bootsLoc, self)
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
        self.app.add_url_rule('/joinP2P', 'join_P2P', self.joinP2P, methods=['POST'])
        self.app.add_url_rule('/rb/addNode', 'addNode', self.addNode, methods = ['POST'])
        self.app.add_url_rule('/rb/rmNode', 'rmNode', self.rmNode, methods = ['DELETE'])
        self.app.add_url_rule('/rb/addTransaction', 'addTransaction', self.addTransaction, methods = ['POST'])
        self.app.add_url_rule('/rb/blockMined', 'blockMined', self.blockMined, methods = ['POST'])
        self.app.add_url_rule('/askBC', 'askBC', self.askBC, methods = ['GET'])

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

        """
        blocks = self.peer._blockchain._blocks
        HblockChain = blocks[len(blocks) - 1]._hash
        return json.dumps(HblockChain)
        """
        return json.dumps('')

    def rmNode(self):
        node = request.get_json()
        self.peer.rb.rbHandler('DELETE', '/rb/rmNode', node)
        self.peer.pfd.rm_node(node)
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

    def askBC(self):
        return self.peer._blockchain.toJson2()


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
        self.peer.rb.broadcast("POST","/rb/addNode", self.bootsLoc)

        """
        listH = np.zeros((len(objH), 2))
        for i in np.arange(len(objH)):
            listH[i][0] = json.loads(objH)[i][0]
            listH[i][1] = json.loads(objH)[i][1]

        unique, counts = np.unique(listH[:][0], return_counts=True)
        secureH = unique[np.argmax(counts)]

        #take the first secureNode from secureH
        secureNode = listH[listH[:][0].index(secureH)][1]

        objBC = self.peer.pl.send(secureNode, "GET", "/askBC", '')

        self.peer._blockchain.setStorage(objBC)
        """

    def broadcastTransaction():
        #TODO when broadcast available
        pass

    def broadcast_foundBlock(self, block):

        pass

    def disconnect(self):
        objNodes = self.peer.pl.send(bootsDist, "DELETE", "/rmNode", self.bootsLoc)
        objH = self.Peer.rb.broadcast("DELETE", "/rb/rmNode", self.bootsLoc)


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
