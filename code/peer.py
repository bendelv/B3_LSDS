from flask import Flask, request
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
        server = Thread(target = self.launchServer, args=address)
        server.start()
        pass

    def launchServer(self, address):
        self.app = Flask(__name__)
        self.app.add_url_rule('/getBlockChain', 'coucou', self.sendBlockChain)
        self.app.add_url_rule('/addNode/', 'addNode', self.addNode)
        self.app.add_url_rule('/rmNode/', 'rmNode' self.rmNode, methods = ['POST'])

        myList = address.split(':')
        host = myList[0]
        port = myList[1]
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def sendBlockChain(self):
        return "coucou"

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


    def getCurrBlockChain(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("GET","/getBlockChain")
        res = conn.getresponse()
        print(res.read())

    def broadcast(self, method, url):
        for connected in self.connected:
            conn = httplib.HTTPConnection("{}".format(connected))
            conn.request(method, url.format(connected))
            res = conn.getresponse()

    def fetchConnected(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("POST","/newAddress/?address={}".format(self.boots))
        jsonConnected = conn.getresponse().read()
        self.connected = json.loads(jsonConnected)
        print(self.connected)

    def disconnect(self):
        conn = httplib.HTTPConnection("{}".format(self.bootsDist))
        conn.request("DELETE","/rmNode/?address={}".format(self.bootsLoc))
        print(conn.getresponse().read())
        #TODO: broadcast disconnect to every node
        broadcast('DELETE', "/rmNode/?address={}")

    def addNode(self, address):
        if address not in self.connected:
            self.connected.append(address)
            print("node {} added".format(address))
        pass

    def rmNode(self, address):
        if address in self.connected:
            self.connected.remove(address)
            print("node {} removed".format(address))
        pass

def main():
    peer = Peer(('192.168.1.25:5000'), ('192.168.1.60:5000'))
    peer.removeConnection()
    return 0

if __name__ == "__main__":
    main()
