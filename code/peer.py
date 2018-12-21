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
        self.bootsLoc = bootsLoc# DEPRECATED USE self.own
        self.own = "{}".format(bootsLoc)
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
        self.clientSide.disconnect()
        self.serverSide.disconnect()

    def broadcastFoundBlock(self, block):
        self.clientSide.broadcastFoundBlock(block)

    def broadcastTransaction(self, transaction):
        self.clientSide.broadcastTransaction(transaction)


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
        self.app.add_url_rule('/rb/bestChain', 'bestChain', self.bestChain, methods = ['GET'])
        self.app.add_url_rule('/askBC', 'askBC', self.askBC, methods = ['GET'])
        self.app.add_url_rule('/askBlocks', 'askBlocks', self.askBlocks, methods = ['GET'])
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

        if self.peer._blockchain.length() > 1:
            return json.dumps([self.peer._blockchain.getHash(),
                               self.peer._blockchain.getTransactions()],
                                default=lambda o: o.__dict__,
                                indent=4,
                                sort_keys=True)

        return json.dumps([None, self.peer._blockchain.getTransactions()],
                          default=lambda o: o.__dict__,
                          indent=4,
                          sort_keys=True)

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
        return self.peer._blockchain.toJson2()

    def bestChain(self):
        return json.dumps([self.peer._blockchain.getHash(),
                          self.peer._blockchain.getLen()],
                          default=lambda o: o.__dict__,
                          indent=4,
                          sort_keys=True)

    def askBlocks(self):
        request = request.get_json()
        block_index = request[0]['msg']
        blocks = self.peer._blockchain._blocks[block_index:]
        return json.dumps(blocks,
                          default=lambda o: o.__dict__,
                          indent=4,
                          sort_keys=True)

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

        if not res:
            return

        hashes = np.array([x[0][0] for x in res],dtype=object)
        processes = np.array([x[1] for x in res],dtype=object)
        all_transactions = np.array([x[0][1] for x in res],dtype=object)
        for transactions in all_transactions:
            for transaction in transactions:
                t = blockchain.Transaction.fromJsonDict(transaction)
                self.peer._blockchain.addTransaction(t, False)

        # No block in the chain for now
        hashes[np.where(hashes == None)] = ''
        unique, index, counts = np.unique(hashes, return_counts=True, return_index=True)
        counts, unique, index = (list(x) for x in zip(*sorted(zip(counts, unique, index))))
        best_hash = unique[0]
        best_process = processes[index[0]]

        if best_hash == '':
            # We only have '' in the list of hashes, else there is at leaste a
            # hash that is usable
            if len(counts) == 1:
                return
            else:
                best_hash = unique[1]
                best_process = processes[index[1]]
        blocks = self.peer.pl.send(self.peer.own, best_process, "GET", "/askBC", '')

        if blocks is not None:
            self.peer._blockchain.setStorage(blocks)

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
