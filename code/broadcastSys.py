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
        self.app.run(debug=False, use_reloader=False, host=self.host, port=self.port)

    def shutdown(self):
        self.shutdown_server()
        return 'Server shutting down...'
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()


class ReliableBroadcast(Layer):
    def __init__(self, own, processes, flaskApp, suscriber):
        super().__init__(suscriber)
        self.own = own
        self.pl = PerfectLink(flaskApp)
        self.correct = processes
        self.msg_from = {}
        for p in processes:
            self.msg_from[p] = []
        self.pfd = PerfecFailureDetector(own, processes, 5, flaskApp, self)
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
            respList.append(self.pl.send(p, method, url, json.dumps(msg))

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


class PerfecFailureDetector(Layer):
    def __init__(self, own, alive, timeout, flaskApp, suscriber):
        super().__init__(suscriber)
        self.pl = PerfectLink(flaskApp)
        self.own = own
        self.process = alive.copy()
        self.alive = alive.copy()
        self.detected = []
        self.now_alive = alive.copy()
        flaskApp.add_url_rule('/FailurDetector/deliver', 'pfd_delivering', self.deliver, methods=['POST'])
        flaskApp.add_url_rule('/FailurDetector/see', 'pfd_see', self.status, methods=['GET', 'POST'])
        self.timeout = timeout
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()

    def notify(self, message):
        pass
    #trigger functionallity
    def deliver(self):
        dict = request.get_json()
        # upon event deliver heartbeatRequest
        if dict['message'] == "request":
            if dict['from'] not in self.process:
                self.process.append(dict['from'])
                self.alive.append(dict['from'])
            self.send_heartbeat_reply(dict['to'], dict['from'])
        # upon event deliver heartbeatReply
        elif dict['message'] == "reply":
            self.alive.append(dict['from'])

        return ""

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

    def timeoutCallback(self):
        self.now_alive = self.alive.copy()
        for p in self.detected.copy():
            self.rm_node(p)
        for p in self.process:
            if (p not in self.alive) and (p not in self.detected):
                self.detected.append(p)
                if self.suscriber is not None:
                    dict = {}
                    dict['process'] = p
                    dict['layer'] = 'pfd'
                    self.trigger(dict)
            heartBeat = Thread(target = self.send_heartbeat_request, args =[self.own, p])
            if p in self.alive:
                self.alive.remove(p)
            heartBeat.start()
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()
        # used for printing
        self.time = time.time()
        pass
    # own sends heartBeat request to process
    def send_heartbeat_request(self, own, process):
        dict = {}
        dict['from'] = own
        dict['to'] = process
        dict['message'] = 'request'
        self.pl.send(process, "POST", "/FailurDetector/deliver", json.dumps(dict))
        pass
    # own send heartBeat reply to process
    def send_heartbeat_reply(self, own, process):
        dict = {}
        dict['from'] = own
        dict['to'] = process
        dict['message'] = 'reply'
        self.pl.send(process, "POST", "/FailurDetector/deliver", json.dumps(dict))
        pass


class FailureDetector(Layer):
    def __init__(self, own, alive, timeout, flaskApp):
        self.pl = PerfectLink(flaskApp)
        self.own = own
        self.alive = alive.copy()
        self.now_alive = alive.copy()
        flaskApp.add_url_rule('/FailurDetector/deliver', 'deliver', self.deliver, methods=['POST'])
        flaskApp.add_url_rule('/FailurDetector/see', 'see', self.status, methods=['GET', 'POST'])
        self.process = alive.copy()
        self.suspected = {}
        self.timeout = timeout
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()

        # used for printing
        self.time = time.time()

    def notify(message):
        pass
    #trigger functionallity
    def deliver(self):
        dict = request.get_json()
        # upon event deliver heartbeatRequest
        if dict['message'] == "request":
            self.send_heartbeat_reply(dict['to'], dict['from'])
        # upon event deliver heartbeatReply
        elif dict['message'] == "reply":
            self.alive.append(dict['from'])

        return ""

    def get_alive(self):
        return self.now_alive

    def rm_node(self, process):
        if process in self.process:
            self.process.remove(process)
        if process in self.alive:
            self.alive.remove(process)
        if process in self.suspected:
            del self.suspected[process]

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
        ulS = "<h2>Suspects</h2><ul>" + "\n".join(["<li>" + x + "</li>" for x in self.suspected]) + "</ul>"
        ulP = "<h2>Process</h2><ul>" + "\n".join(["<li>" + x + "</li>" for x in self.process]) + "</ul>"
        return title + timeout + ulA + ulS + ulP

    def timeoutCallback(self):
        self.now_alive = self.alive.copy()
        if len(list(set(self.alive) & set(self.suspected.keys()))) == 0:
            self.timeout += 0
        for p in self.process:
            if (p not in self.alive) and (p not in self.suspected.keys()):
                self.suspected[p] = 0
            elif p in self.alive and p in self.suspected.keys():
                del self.suspected[p]
            elif p in self.suspected.keys():
                # Fail stop hypothesis. after 5 non heartbeat request, remove node.
                self.suspected[p] += 1
                if self.suspected[p] > 5:
                    self.rm_node(p)
                    # trigger upper layers
                    self.trigger(p)
            heartBeat = Thread(target = self.send_heartbeat_request, args =[self.own, p])
            if p in self.alive:
                self.alive.remove(p)
            heartBeat.start()
        self.t = Timer(self.timeout, self.timeoutCallback)
        self.t.start()
        # used for printing
        self.time = time.time()
        pass
    # own sends heartBeat request to process
    def send_heartbeat_request(self, own, process):
        dict = {}
        dict['from'] = own
        dict['to'] = process
        dict['message'] = 'request'
        self.pl.send(process, "POST", "/FailurDetector/deliver", json.dumps(dict))
        pass
    # own send heartBeat reply to process
    def send_heartbeat_reply(self, own, process):
        dict = {}
        dict['from'] = own
        dict['to'] = process
        dict['message'] = 'reply'
        self.pl.send(process, "POST", "/FailurDetector/deliver", json.dumps(dict))
        pass


class PerfectLink(Layer):
    def __init__(self, flaskApp):
        super().__init__(None)
        flaskApp.add_url_rule('/PerfectLink/',
                              self.plDeliver,
                              methods=['POST'])
        pass

    #send message: message from process: own to process: process
    def send(self, process, method, url, data):
        # TODO handle exceptions like wrong address
        try:
            conn = httplib.HTTPConnection(process, timeout=10)
            conn.request(method, url, data,  {'content-type': 'application/json'})
            response = conn.getresponse().read()
        except:
            return None
        return (response.decode(), process)

    #Process delivered message correctly to own
    def plDeliver(self):
        args = request.args
        message = request.get_json()
        self.trigger(message)
        return ""

    def notify(self, message):
        pass


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--address", type=str, default="192.168.1.25",
                        help="ip Address")
    parser.add_argument("--port", type=str, default="5001",
                        help="Port number")
    arguments, _ = parser.parse_known_args()

    return arguments


def main(args):
    app0 = App("192.168.1.25", "5000")
    app1 = App("192.168.1.25", "5001")
    app2 = App("192.168.1.25", "5002")
    #process = ["192.168.1.25:5000", "192.168.1.25:5001"]
    process = ["192.168.1.25:5000", "192.168.1.25:5001", "192.168.1.25:5002"]
    #f0 = PerfecFailureDetector(process[0], process, 2, app0.app, None)
    #f1 = PerfecFailureDetector(process[1], process, 5, app1.app, None)
    #f2 = PerfecFailureDetector(process[2], process, 5, app2.app, None)
    rb0 = ReliableBroadcast(process[0], process, app0.app, None)
    rb1 = ReliableBroadcast(process[1], process, app1.app, None)
    rb2 = ReliableBroadcast(process[2], process, app2.app, None)
    app0.launchServer()
    app1.launchServer()
    app2.launchServer()
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

if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
    print("EXIT MAIN !!!!")
