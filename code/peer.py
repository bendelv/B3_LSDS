from flask import Flask, request
from argparse import ArgumentParser, ArgumentTypeError
from threading import Thread
import http.client as httplib
import json
import time

class Peer:
    def __init__(self, bootsDist, bootsLoc):
        self.serverSide = Server(bootsLoc, self)
        self.clientSide = Client(bootsDist, bootsLoc)
        pass

    def removeConnection(self):
        self.clientSide.disconnect()

class Server:
    def __init__(self, address, peer):
        self.peer = peer
        server = Thread(target = self.launchServer, args=[address])
        server.start()
        pass

    def launchServer(self, args):

        address = args
        self.app = Flask(__name__)
        self.app.add_url_rule('/addNode/', 'addNode', self.addNode)
        self.app.add_url_rule('/rmNode/', 'rmNode', self.rmNode, methods = ['POST'])

        myList = address.split(':')
        host = myList[0]
        port = myList[1]
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def addNode(self):
        address = request.args.get('address', '')
        self.peer.clientSide.addNode(address)

        return "node {} added".format(address)

    def rmNode(self):
        address = request.args.get('address', '')
        self.peer.clientSide.rmNode(address)

        return "node removed"

class Client:
    def __init__(self, bootsDist, bootsLoc):
        self.bootsDist = bootsDist
        self.bootsLoc = bootsLoc

        self.connected = self.fetchConnected()
        self.connectToNodes()

    def broadcast(self, method, url, address):
        for connected in self.connected:
            if connected != self.bootsLoc:
                conn = httplib.HTTPConnection("{}".format(connected))
                conn.request(method, url.format(address))
                print(conn.getresponse().read())

    def fetchConnected(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("POST","/addNode/?address={}".format(self.bootsLoc))

        jsonConnected = conn.getresponse().read()

        return (json.loads(jsonConnected))

    def connectToNodes(self):
        self.broadcast("POST","/addNode/?address={}", self.bootsLoc)

    def disconnect(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("DELETE","/rmNode/?address={}".format(self.bootsLoc))
        print(conn.getresponse().read())
        #TODO: broadcast disconnect to every node
        self.broadcast('DELETE', "/rmNode/?address={}", self.bootsLoc)

    def addNode(self, address):
        if address not in self.connected:
            self.connected.append(address)
            print("node {} added".format(address))
        pass

    def rmNode(self, address):
        if address in self.connected and (not bootsLoc):
            if address == bootsLoc:
                print(bootsLoc)
            print("node {} removed".format(address))
            self.connected.remove(address)
        pass

def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--locport',
        default="8001")
    args = parser.parse_args()

    bootsDist = "192.168.1.50:8000"
    bootsLoc = "192.168.1.50:{}".format(args.locport)
    peer1 = Peer(bootsDist, bootsLoc)

    input()
    peer1.removeConnection()
    return 0

if __name__ == "__main__":
    main()
