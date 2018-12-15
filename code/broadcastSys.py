from flask import Flask, request
import http.client as httplib
from threading import Thread
import time
from threading import Timer
import threading
import json
import numpy as np
import argparse

from abc import ABC, abstractmethod

# Implements trigger mechanisme
class Layer(ABC):
    def __init__(self, suscriber):
        self.suscriber = suscriber

    @abstractmethod
    def notify(self, message):
        pass

    def trigger(self, message):
        if self.suscriber is not None:
            self.suscriber.notify(message)


class App(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.add_url_rule('/shutdown_server/', 'server', self.shutdown, methods=['GET'])

    def launchServer(self):
        server = Thread(target = self.launchServerNow, args =[])
        server.start()
        time.sleep(1)

    def launchServerNow(self):
        print(self.host, self.port)
        self.app.run(debug=False, use_reloader=False, host=self.host, port=self.port)

    def shutdown(self):
        self.shutdown_server()
        return 'Server shutting down...'
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

class fakePeer(object):
    def __init__(self, host, port, alive):
        self.app = App(host, port)
        self.bootsLoc = "{}:{}".format(host, port)
        self.pl = PerfectLink()
        self.pfd = PerfecFailureDetector(alive, 5, self)
        #self.rb = ReliableBroadcast("{}".format(bootsLoc),  ["{}".format(bootsLoc)], self.serverSide.app, self)

        self.app.launchServer()

class ReliableBroadcast():
    def __init__(self, own, processes, peer):
        super().__init__(suscriber)
        self.own = own

        self.correct = processes
        self.msg_from = {}

        for p in processes:
            self.msg_from[p] = []

        self.pfd = peer.pfd
        self.pl = peer.pl
        flaskApp.add_url_rule('/rb/see', 'rb_see', self.status, methods=['GET'])

    def status(self):
        def print_msg(msgs, p):
            view = "Process: {}<ul>".format(p)
            if len(msgs) > 0:
                for msg in msgs:
                    view += "<li> Message <ul>"
                    view += "<li><b> Timestamp: </b>{}</li>".format(msg['ts'])
                    view += "<li><b> Message: </b>{}</li></ul>".format(msg['msg'])
            else:
                view += "<li> Message <ul>"
                view += "<li><b> None </b></li>"
            view += "</ul></li></ul>"
            return view

        title = "<h1> log page RB broadcast</h1>"
        list = "<h2> Messages recieved</h2>"+ "\n".join([print_msg(self.msg_from[p], p) for p in self.correct])
        return title + list + self.pfd.status()

    def broadcast(self, method, url, msg):
        dict = {}
        dict['from'] = self.own
        dict['msg'] = message

        return self._broadcast(method, url, dict)

    def _broadcast(self, method, url, msg):
        respList = []
        for p in self.correct:
            respList.append(self.pl.send(p, method, url, msg))

        return respList

    def notify(self, msg):
        dict = msg
        if 'layer' in dict.keys():
            layer = dict['layer']
            if layer == 'pfd':
                p = dict['process']
                self.pfdHandler(p)
    #upon event beb deliver
    def rbHandler(self, p, method, url, msg):
        if msg not in self.msg_from[p]:
            self.msg_from[p].append(msg)
            msg['layer'] = 'rb'
            self.trigger(msg)
            if p not in self.correct:
                self._broadcast(method, url, msg)
    #upon event crash p
    def pfdHandler(self, p):
        if p in self.correct:
            self.correct.remove(p)
        for msg in self.msg_from[p]:
            self._broadcast(msg['method'], msg['url'], msg['msg'])


class PerfecFailureDetector():
    def __init__(self, alive, timeout, peer):

        flaskApp = peer.app.app
        self.pl = peer.pl
        self.own = peer.bootsLoc

        self.process = alive.copy()
        self.alive = alive.copy()
        self.detected = []
        self.now_alive = alive.copy()

        flaskApp.add_url_rule('/FD/heartbeatRequest', 'heartbeat', self.heartbeatReply, methods=['GET'])
        flaskApp.add_url_rule('/FD/see', 'status', self.status, methods=['GET'])
        self.timeout = timeout
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()

    def get_alive(self):
        return self.now_alive

    def rm_node(self, process):
        if process in self.process:
            self.process.remove(process)
        if process in self.alive:
            self.alive.remove(process)
        if process in self.detected:
            self.detected.remove(process)

    def add_node(self, process):
        if process not in self.process:
            self.process.append(process)
        if process not in self.alive:
            self.alive.append(process)

    def status(self):
        # optimization, implement nodes as a dict for a lookup in O(1) instead
        # of O(n), OKAY here as we assume a small amount of nodes
        title = "<h1> Status of the perfect detectors, Timeout {}</h1>".format(self.timeout)
        timeout = "<h2> Time: {0:.2f}</h2>".format(time.time() - self.time)
        ulA = "<h2>alive</h2><ul>" + "\n".join(["<li>" + x + "</li>" for x in self.alive]) + "</ul>"
        ulS = "<h2>Detected</h2><ul>" + "\n".join(["<li>" + x + "</li>" for x in self.detected]) + "</ul>"
        ulP = "<h2>Process</h2><ul>" + "\n".join(["<li>" + x + "</li>" for x in self.process]) + "</ul>"
        return title + timeout + ulA + ulS + ulP

    def heartbeatRequest(self, p):
        if p in self.alive:
            self.alive.remove(p)
        alive = self.pl.send(p, 'GET', '/FD/heartbeatRequest', '', self.timeout -0.05)
        if alive is not None:
            load = json.loads(objAlive)

            if load is 'True':
                self.alive.append(p)

    def heartbeatReply(self):
        print("HERE")
        list = request.get_json()
        p = list[1]
        if p not in self.process:
            self.add_node(p)
        return json.dumps('True')

    def timeoutCallback(self):
        print("enter callback")
        self.now_alive = self.alive.copy()
        for p in self.detected.copy():
            if p not in self.alive:
                self.rm_node(p)

        for p in self.process:
            if (p not in self.alive) and (p not in self.detected):
                self.detected.append(p)
            print('FDP')
            objAlive = Thread(target = self.heartbeatRequest, args = [p])
            objAlive.start()

        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()
        # used for printing
        self.time = time.time()
        pass
    # own send heartBeat reply to process

class PerfectLink():
    def __init__(self):
        pass

    #send message: message from process: own to process: process
    def send(self, process, method, url, data, timeout=10):
        # TODO handle exceptions like wrong address
        #try:
        print(process)
        conn = httplib.HTTPConnection(process, timeout)
        arr = [data, process]
        print(method)
        print(url)
        print(json.dumps(arr))
        conn.request(method, url, json.dumps(arr),  {'content-type': 'application/json'})
        response = conn.getresponse().read()
        #except:
        return None
        return response.decode()


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--address", type=str, default="192.168.1.60",
                        help="ip Address")
    parser.add_argument("--port", type=str, default="5000",
                        help="Port number")

    return parser.parse_args()


def main(args):

    alive =["192.168.1.60:5000", "192.168.1.60:5001", "192.168.1.60:5002"]
    fake_peer = fakePeer(args.address, args.port, alive)

    """
    rb0 = ReliableBroadcast(process[0], process, app0.app, None)
    rb1 = ReliableBroadcast(process[1], process, app1.app, None)
    rb2 = ReliableBroadcast(process[2], process, app2.app, None)

    dict = {}
    dict['ts'] = time.time()
    dict['msg'] = "Some broadcasted message 1"
    rb1.broadcast(dict)
    dict['ts'] = time.time()
    dict['msg'] = "Some broadcasted message 2"
    rb1.broadcast(dict)
    dict['ts'] = time.time()
    dict['msg'] = "Some broadcasted message 3"
    rb1.broadcast(dict)
    """

if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
    print("EXIT MAIN !!!!")
