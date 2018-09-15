#!/usr/bin/env python3

import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from time import sleep

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sekrit'
socketio = SocketIO(app)


@socketio.on('echo-back')
def handle_message(client, message):
    string = 'got message "{}" from {}'.format(message, client)
    print(string)
    return string


@socketio.on('async-echo-back')
def handle_async_message(client, message):
    string = 'got message "{}" from {}'.format(message, client)
    print(string)
    sleep(5)
    emit('async back', string)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.debug = True
    socketio.run(app)