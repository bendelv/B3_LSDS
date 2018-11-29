from flask import Flask, request
import http.client as httplib

app = Flask(__name__)

@app.route('/connectedUsers')
def index():
    return 'Hello world'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

