from flask import Flask, request, jsonify
from argparse import ArgumentParser, ArgumentTypeError
from threading import Thread
import http.client as httplib
import numpy as np
import json
import time


import blockchain
from broadcastSys import ReliableBroadcast
from broadcastSys import PerfecFailureDetector
from broadcastSys import PerfectLink

class Peer:
    def __init__(self, blockchain, bootsDist, bootsLoc):
        self._blockchain = blockchain
        self.bootsLoc = bootsLoc# DEPRECATED USE self.own
        self.own = "{}".format(bootsLoc)
        self.bootsDist = bootsDist

        self._server = Server(bootsLoc, self)
        time.sleep(1)
        self.pl = PerfectLink()
        self.pfd = PerfecFailureDetector(["{}".format(bootsLoc)], 5, self)
        self.rb = ReliableBroadcast("{}".format(bootsLoc), self)
        time.sleep(2)
        self._client = Client(bootsDist, bootsLoc, self)
        pass

    def removeConnection(self):
        self._client.disconnect()
        self._server.disconnect()

    def broadcastFoundBlock(self, block):
        self._client.broadcastFoundBlock(block)

    def broadcastTransaction(self, transaction):
        self._client.broadcastTransaction(transaction)

    def askBC(self):
        return self._client.askBC()

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
        self.app.add_url_rule('/rb/askBC', 'askBC', self.askBC, methods = ['GET'])
        self.app.add_url_rule('/view', 'view', self.view, methods = ['GET'])
        self.app.add_url_rule('/disconnect', 'disconnect', self.disconnect, methods = ['POST'])
        myList = address.split(':')
        host = myList[0]
        port = myList[1]
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def joinP2P(self):
        objNode = request.get_json()
        self.peer.pfd.add_node(objNode[0])
        list = self.peer.pfd.get_alive()
        return json.dumps(list, sort_keys=True)

    def addNode(self):
        objNode = request.get_json()
        self.peer.pfd.add_node(objNode[0]['msg'])
        self.peer.rb.rbHandler(objNode[1], 'POST', '/rb/addNode', objNode[0])
        return self.askBC()

    def rmNode(self):
        objNode = request.get_json()
        self.peer.rb.rbHandler(objNode[1], 'DELETE', '/rb/rmNode', objNode[0])
        self.peer.pfd.rm_node(objNode[0]['msg'])
        return json.dumps('', sort_keys=True)
    #To be tested when broadcast available
    def addTransaction(self):
        objTransaction = request.get_json()
        self.peer.rb.rbHandler(objTransaction[1], 'POST', '/rb/addTransaction', objTransaction[0])
        self.peer._blockchain.addLocTransaction(objTransaction[0]['msg'])
        return json.dumps('', sort_keys=True)

    def blockMined(self):
        objBlock = request.get_json()
        self.peer.rb.rbHandler(objBlock[1], 'POST', '/rb/blockMined', objBlock[0])
        self.peer._blockchain.setBlockReceived(objBlock[0]['msg'])
        return json.dumps('', sort_keys=True)

    def askBC(self):
        req = request.get_json()
        self.peer.rb.rbHandler(req[1], 'GET', '/rb/askBC', req[0])
        return self.peer._blockchain.toJson2()

    def view(self):
        title = "<h1> log page Blockchain</h1>"
        return title + self.peer._blockchain.toHtml()

    def disconnect(self):
        self.shutdown_server()
        return 'Server shutting down...'

    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()


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

        for chain in res:
            for transaction in chain[0][1]:
                t = blockchain.Transaction.fromJsonDict(transaction)
                self.peer._blockchain.addTransaction(t, False)

        self.handle_conflict(res)
        return

        if blocks is not None:
            self.peer._blockchain.setStorage(blocks)

    def askBC(self):
        res = self.peer.rb.broadcast('GET', '/rb/askBC', '')
        self.handle_conflict(res)

    def handle_conflict(self, res):
        if not res:
            return
        res.append([json.loads(self.peer._blockchain.toJson2()), "own"])
        length = []
        for chain in res:
            if chain is not None:
                blocks = chain[0][0]
                length.append(len(blocks))

        length = np.array(length)
        secure_l = np.max(length)
        i = np.argmax(length)

        secure_BC = res[i][0]
        if secure_BC is not None:
            self.peer._blockchain.setStorage(secure_BC)

    def broadcastTransaction(self, transaction):
        self.peer.rb.broadcast("POST", '/rb/addTransaction', transaction.toJson())
        pass

    def broadcastFoundBlock(self, block):
        self.peer.rb.broadcast("POST", '/rb/blockMined', block.toJson())
        pass

    def disconnect(self):
        objH = self.peer.rb.broadcast("DELETE", "/rb/rmNode", self.bootsLoc)
        self._peer.pl.send()
        pass


def main(args):

    bootsDist = "192.168.1.41:8000"
    bootsLoc = "192.168.1.41:{}".format(args.bootsloc)
    peer = Peer(bootsDist, bootsLoc)

    return 0

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '--port',
        default="8000")
    args = parser.parse_args()
    main(args)
