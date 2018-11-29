from flask import Flask, request
import http.client as httplib


if __name__ == '__main__':

    conn = httplib.HTTPConnection("0.0.0.0:5000")
    conn.request("GET","/connectedUsers")
    res = conn.getresponse()
    print(res.read())
