"""
Entry point for the web app
"""

# FIXME https://flask.palletsprojects.com/en/2.0.x/quickstart/#a-minimal-application

from flask import Flask, request, send_from_directory
import os

_script_dir = os.path.dirname(__file__)
_react_build_dir = os.path.join(_script_dir, '..', '..', 'build')
print(f"_react_build_dir: {_react_build_dir}")

# https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
app = Flask(__name__, static_url_path=_react_build_dir)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# @app.route('/ui/<path:path>')

# Ok as http://127.0.0.1:5000/index.html, pero queria añadir prefijo de otro tipo

# Ok at http://127.0.0.1:5000/api
@app.route("/api")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory(
        _react_build_dir, path, as_attachment=False
    )
    # return send_from_directory('build', path)


# from flask import Flask, request, send_from_directory

# # set the project root directory as the static folder, you can set others.
# app = Flask(__name__, static_url_path='')

# @app.route('/js/<path:path>')
# def send_js(path):
#     return send_from_directory('js', path)

'''
 Run with: 

# No need as this file is named `app.py`
# export FLASK_APP=
cd online-temp-metrics-webapp
flask run
 
Running on http://127.0.0.1:5000/

'''


---

@app.route("/api")
def hello_world():
    return "<p>Hello, World!</p>"

