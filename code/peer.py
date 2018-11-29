from flask import Flask, request
from threading import Thread
import http.client as httplib
import json
import time

class Peer:
    def __init__(self, bootsDist, bootLoc):
        self.serverSide = Server(bootsLoc[0], bootsLoc[1])
        self.clientSide = Client(bootsDist[0], bootsDist[1])
        pass

class Server:
    def __init__(self, host, port):
        server = Thread(target = self.launchServer, args = (host, port))
        server.start()
        pass

    def launchServer(self, host, port):
        self.app = Flask(__name__)
        self.app.add_url_rule('/getBlockChain', 'coucou', self.sendBlockChain)
        self.app.add_url_rule('/addPeer/<newPeer>', 'addpeer', self.addPeer)
        self.app.add_url_rule('/rcvMsg/', 'rcvmsg', self.rcvMsg, methods = ['POST'])

        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def sendBlockChain(self):
        return "coucou"

    def addPeer(self):
        pass

    def rcvMsg(self):
        msg = request.args.get('msg', '')
        print(msg)
        return "msg received"

class Client:
    def __init__(self, host, port):
        self.connected = []
        pass

    def getBlockChain(self):
        conn = httplib.HTTPConnection("{}:{}".format(self.host, self.port))
        conn.request("GET","/getBlockChain")
        res = conn.getresponse()
        print(res.read())

    def broadcast(self, msg):
        for connected in self.connected:
            conn = httplib.HTTPConnection("{}".format(connected))
            conn.request("POST", "/rcvMsg/?msg={}".format(msg))
            res = conn.getresponse()

    def fetchConnected(self):
        conn = httplib.HTTPConnection("{}:{}".format(self.host, self.port))
        conn.request("GET","/getBlockChain")
        res = conn.getresponse()

def main():
    peer = Peer('192.168.1.60', 5000)
    time.sleep(2)
    peer.clientSide.broadcast("Coucou")
    return 0

if __name__ == "__main__":
    main()
