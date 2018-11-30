from flask import Flask, request
import http.client as httplib
from threading import Thread
import time

BootstrapAdd = "192.168.1.25:5000"

'''
conn = httplib.HTTPConnection(BootstrapAdd)
conn.request("POST",'/newAddress/?address=someAdd')
res = conn.getresponse()
print(res.read())
conn = httplib.HTTPConnection(BootstrapAdd)
conn.request("POST",'/newAddress/?address=someAdd4')
res = conn.getresponse()
print(res.read())
conn = httplib.HTTPConnection(BootstrapAdd)
conn.request("POST",'/newAddress/?address=someAdd1')
res = conn.getresponse()
print(res.read())
conn = httplib.HTTPConnection(BootstrapAdd)
conn.request("POST",'/newAddress/?address=someAdd3')
res = conn.getresponse()
print(res.read())
input()

conn = httplib.HTTPConnection(BootstrapAdd)
'''
#conn.request("DELETE",'/rmAddress/?address=someAdd1')
'''
res = conn.getresponse()
print(res.read())

input()
conn = httplib.HTTPConnection(BootstrapAdd)
'''
#conn.request("DELETE",'/rmAddress/?address=someAdd1')
'''
res = conn.getresponse()
print(res.read())
'''

from flask import Flask, request
import http.client as httplib
from threading import Thread
import time
from threading import Timer
import threading
import json

from flask import Flask, request
import http.client as httplib
from threading import Thread
import time
from threading import Timer
import threading
import json

class App(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = Flask(__name__)

    def launchServer(self):
        server = Thread(target = self.launchServerNow, args =[])
        server.start()
        time.sleep(1)

    def launchServerNow(self):
        self.app.run(debug=False, use_reloader=False, host=self.host, port=self.port)


class BroadCast:
    def __init__(self, peer_list):
        self.peer_list = peer_list
        "retrieve all connected adress nodes from bootstrap node"
        pass

    def broadcast(self, method, message):
        "Send a json object to all connected user"
        pass


class FailurDetector(object):
    def __init__(self, own, alive, suspected, timeout, server):

        server.app.add_url_rule('/aliveSuspectsProcess/', 'status', self.status, methods=['GET'])
        server.app.add_url_rule('/', 'home', self.ping, methods=['GET', 'POST'])
        server.launchServer()
        self.own = own
        self.pl = PerfectLink()
        self.alive = alive.copy()
        self.alive.remove(self.own)
        self.process = alive.copy()
        self.process.remove(self.own)
        self.suspected = suspected
        self.timeout = timeout
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()

    def ping(self):
        return "PING PAGE"

    def status(self):
        print(self.alive)
        print(self.suspected)
        print(self.process)
        # optimization, implement nodes as a dict for a lookup in O(1) instead
        # of O(n), OKAY here as we assume a small amount of nodes
        title = "<h1> Status of the perfect detectors </h1>"
        ulA = "<ul>" + "\n".join(["<li>" + x + "</li>" for x in self.alive]) + "</ul>"
        ulS = "<ul>" + "\n".join(["<li>" + x + "</li>" for x in self.suspected]) + "</ul>"
        ulP = "<ul>" + "\n".join(["<li>" + x + "</li>" for x in self.process]) + "</ul>"
        return title + "<h2>alive</h2>" + ulA + "<h2>Suspects</h2>" + ulS + "<h2>Process</h2>" + ulP

    def add_node(self, node):
        self.process.append(node)

    def remove_node(self, node):
        if node in self.process:
            self.process.remove[node]
        if node in self.alive:
            self.alive.remove[node]
        if node in self.alive:
            self.suspect.remove[node]

    def timeoutCallback(self):
        if len(list(set(self.alive) & set(self.suspected))) == 0:
            self.timeout += 1
        for p in self.process:
            if (p not in self.alive) and (p not in self.suspected):
                self.suspected.append(p)
            elif p in self.alive and p in self.suspected:
                self.suspected.remove(p)
            heartBeat = Thread(target = self.send_heartbeat_request, args =[self.own, p])
            if p in self.alive:
                self.alive.remove(p)
            heartBeat.start()
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()
        pass
    # own sends heartBeat request to process
    def send_heartbeat_request(self, own, process):
        res, _, _, _ = self.pl.send(own, "GET", "/", process)
        if res is not None:
            #own delivered request to process
            self.deliver_heartbeat_request(process, own)
        pass
    # own send heartBeat reply to process
    def send_heartbeat_reply(self, own, process):
        res, _, _, _ = self.pl.send(own, "POST", "/", process)
        if res is not None:
            #own delivered request to process
            self.deliver_heartbeat_reply(process, own)
        pass
    # process delivered heartBeat request to own
    def deliver_heartbeat_request(self, own, process):
        #own sends hearbeat reply to process
        self.send_heartbeat_reply(own, process)
        pass
    # process delivered heartbeat reply to own
    def deliver_heartbeat_reply(self, own, process):
        if process not in self.alive:
            self.alive.append(process)
        pass


class PerfectLink(object):
    def __init__(self):
        pass

    #send message: message from process: own to process: process
    def send(self, own, method, message, process, data = None, headers = None):
        # TODO handle exceptions like wring address
        try:
            conn = httplib.HTTPConnection(process, timeout=10)
            if (headers is not None) and (data is not None):
                conn.request(method, message, data, headers)
            else:
                conn.request(method, message)
        except:
            return self.deliver(None, None, None, None)
        rep = conn.getresponse()
        time.sleep(1)
        return self.deliver(rep, message, process, own)

    #Process delivered message correctly to own
    def deliver(self, retrunMessage, message, own, process):
        if retrunMessage is not None:
            #print(retrunMessage.status, retrunMessage.reason)
            return retrunMessage, message, own, process
        else:
            return None, None, None, None



def main():
    print("ADD NODE TIME")
    process = ["10.9.175.1:5000", "10.9.175.1", "10.9.175.1:5002"]
    app2 = App("10.9.175.1", "5002")
    pl2 = PerfectLink()
    f2 = FailurDetector(process[2], process, [], pl2, 5)

if __name__ == '__main__':
    main()
