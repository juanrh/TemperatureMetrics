"""
Entry point for the temperature measurement agent

NOT following https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html,
but this is not a package utils script, but an entry point
for deployment
"""
# pylint: disable=invalid-name

import os
import sys
import logging
import logging.handlers

from invoke import task

from metricsapp import app

_script_dir = os.path.dirname(__file__)
_repo_root_dir = os.path.join(_script_dir, '..',  '..',  '..')
sys.path.append(_repo_root_dir)
from utils.invoke import print_title # pylint: disable=wrong-import-position,wrong-import-order
_app_package_name = 'metricsapp'

def setup_logging():
    """Setup logging"""
    logger = logging.getLogger()
    logger.setLevel('DEBUG')
    formatter = \
        logging.Formatter('%(asctime)s [%(levelname)s] - [%(process)d] - %(name)s: %(message)s')
    def setup_handler(handler):
        handler.setFormatter(formatter)
        handler.setLevel('DEBUG')
        logger.addHandler(handler)
    stdoutHandler = logging.StreamHandler()
    setup_handler(stdoutHandler)

@task
def build(c):
    """Build the app
    - Update the statics folder to the latest version of the frontend"""
    with c.cd(os.path.join(_script_dir, '..', 'frontend')):
        c.run('npm run build')

@task
def run(c):
    """Launch web app to default port at http://127.0.0.1:5000/index.html
    This assumes the React app is built, so it can be served as
    static files

    No need to `export FLASK_APP=` as the main script is named `app.py`
    """
    setup_logging()
    with c.cd(os.path.join(_script_dir, _app_package_name)):
        app.main()

@task
def release(c):
    """Run all tests and all code analysis tools"""
    with c.cd(_script_dir):
        with print_title("Checking types with mypy"):
            c.run(f"mypy --config-file {os.path.join(_script_dir, 'mypy.ini')} {_app_package_name}")
        with print_title("Running pylint linter"):
            pylint_args = f'''--init-hook="sys.path.append('{_repo_root_dir}')"'''
            c.run(f"pylint {pylint_args} tasks.py {_app_package_name}")
