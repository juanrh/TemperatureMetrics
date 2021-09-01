"""
Entry point for the web app
"""

import os

from flask import Flask, send_from_directory


_script_dir = os.path.dirname(__file__)
_react_build_dir = os.path.join(_script_dir, '..', '..', 'frontend', 'build')

app = Flask(__name__, static_url_path=_react_build_dir)

@app.route('/<path:path>')
def serve_frontend_app(path):
    """Server the frontend React app as static files"""
    return send_from_directory(
        _react_build_dir, path, as_attachment=False
    )
