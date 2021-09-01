"""
Entry point for the web app

Websockets events:

- metricsStart: client ask the server to start sending measurements, proving a string
value at field 'hostname'
- metricsStop: client ask the server to stop sending measurements
- metricsMeasurement: server sends a measurement to the client, with fields
    - timestamp: int. As epoch time in milliseconds, as returned by
      `math.floor(time.time_ns() / 1000000)`
    - value: float. Temperature measurement
"""

import os
import logging
import json
import time
import math
from random import uniform

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

_script_dir = os.path.dirname(__file__)
_react_build_dir = os.path.join(_script_dir, '..', '..', 'frontend', 'build')

app = Flask(__name__, static_url_path=_react_build_dir)
# use disconnect() to close the websocket
socketio = SocketIO(app)
logger = logging.getLogger('App')

@app.route('/<path:path>')
def serve_frontend_app(path):
    """Server the frontend React app as static files"""
    return send_from_directory(
        _react_build_dir, path, as_attachment=False
    )

@socketio.on('metricsStart')
def metrics_start(message):
    """Handle event of client asking to start retrieving metrics"""
    logger.info('Got metricsStart message for msg: %s', json.dumps(message))
    timestamp = math.floor(time.time_ns() / 1000000)
    for i in range(10):
        emit('metricsMeasurement', {'timestamp': timestamp + i*20, 'value': uniform(20, 30)})

@socketio.on('metricsStop')
def metrics_stop():
    """Handle event of client asking to stop retrieving metrics"""
    logger.info('Got metricsStop message')

@socketio.on('connect')
def connection_event():
    """Handle event of client connecting"""
    logger.info('Client connected')

@socketio.on('disconnect')
def disconnection_event():
    """Handle event of client disconnecting"""
    logger.info('Client dicconnected')

def main():
    """Entry point of this webapp"""
    logger.info('Starting app at http://127.0.0.1:5000/index.html')
    socketio.run(app)
