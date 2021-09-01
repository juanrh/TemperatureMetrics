"""
Entry point for the temperature measurement agent

NOT following https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html,
but this is not a package utils script, but an entry point
for deployment
"""
# pylint: disable=invalid-name

import os
import sys
from invoke import task

_script_dir = os.path.dirname(__file__)
_repo_root_dir = os.path.join(_script_dir, '..',  '..',  '..')
sys.path.append(_repo_root_dir)
from utils.invoke import print_title # pylint: disable=wrong-import-position
_app_package_name = 'metricsapp'

@task
def run(c):
    """Launch web app to default port at http://127.0.0.1:5000/index.html
    This assumes the React app is built, so it can be served as
    static files

    No need to `export FLASK_APP=` as the main script is named `app.py`
    """
    print('Open app at http://127.0.0.1:5000/index.html')
    with c.cd(os.path.join(_script_dir, _app_package_name)):
        c.run('flask run')

@task
def release(c):
    """Run all tests and all code analysis tools"""
    with c.cd(_script_dir):
        with print_title("Checking types with mypy"):
            c.run(f"mypy --config-file {os.path.join(_script_dir, 'mypy.ini')} {_app_package_name}")
        with print_title("Running pylint linter"):
            pylint_args = f'''--init-hook="sys.path.append('{_repo_root_dir}')"'''
            c.run(f"pylint {pylint_args} tasks.py {_app_package_name}")
