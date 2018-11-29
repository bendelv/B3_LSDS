from flask import Flask
from threading import Thread
import http.client as httplib
import json
import time

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.serverSide = Server(host, port)
        self.clientSide = Client()
        pass

class Server:
    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.app.add_url_rule('/getBlockChain', 'coucou', self.coucou)
        server = Thread(target = self.launchServer, args = (host, port))
        server.start()
        pass

    def launchServer(self, host, port):
        self.app.run(debug=True, use_reloader=False, host=host, port=port)

    def coucou(self):
        return "coucou"

class Client:
    def __init__(self):
        self.connected = ['192.168.1.25:5000', '192.168.1.60:5000']
        pass

    def getBlockChain(self):
        conn = httplib.HTTPConnection("{}:{}".format(self.host, self.port))
        conn.request("GET","/getBlockChain")
        res = conn.getresponse()
        print(res.read())

    def broadcast(self, msg):

        jsonData = json.dumps(msg)
        for connected in self.connected:
            headers = {'Content-type': 'application/json'}
            conn = httplib.HTTPConnection("{}".format(connected))
            conn.request("POST","/post", jsonData, headers)
            res = conn.getresponse()
        pass

def main():
    peer = Peer('localhost', 5000)
    time.sleep(2)
    peer.clientSide.broadcast("Coucou")
    return 0

if __name__ == "__main__":
    main()
