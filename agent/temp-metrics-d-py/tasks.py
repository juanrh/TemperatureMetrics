"""
Entry point for the temperature measurement agent

NOT following https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html,
but this is not a package utils script, but an entry point
for deployment
"""
# pylint: disable=invalid-name

import os
from contextlib import contextmanager
import glob
import json

from invoke import task
from fabric import Config, Connection
from tempd.agent import Main

_script_dir = os.path.dirname(__file__)

def read_conf(path):
    """Read a configuration file"""
    with open(path, 'r') as in_f:
        return json.load(in_f)

@contextmanager
def print_title(message):
    """
    Print a message with a underline chars, so it is more visible, and
    then print some empty lines when leaving this context.
    """
    print(f"{message}")
    print('='*30)
    yield
    print('-'*40)
    print()


@task
def test(c):
    """Run all tests"""
    with c.cd(_script_dir):
        with print_title("Running unit tests"):
            c.run("python setup.py test")

@task
def release(c):
    """Run all tests and all code analysis tools"""
    with c.cd(_script_dir):
        test(c)
        with print_title("Checking types with mypy"):
            c.run(f"mypy --config-file {os.path.join(_script_dir, 'mypy.ini')} tempd")
        with print_title("Running pylint linter"):
            c.run('pylint tasks.py tempd')

@task
def package(c):
    """
    Package the code as wheel (python eggs are deprecated).
    Install resulting package with `pip install dist/tempd-0.1-py3-none-any.whl`
    """
    with c.cd(_script_dir):
        c.run('rm -rf build dist')
        c.run('python setup.py bdist_wheel')
    package_path = glob.glob(os.path.join(_script_dir, 'dist', '*.whl'))[0]
    c.run(f"unzip -l {package_path}")
    return package_path


def connect_with_sudo(config):
    """
    Connects to a remote host with sudo enabled
    """
    sudo_pass = config['agent']['sudo_pass']
    fabric_conf = Config(overrides={'sudo': {'password': sudo_pass}})
    return Connection(config['agent']['host'], config=fabric_conf)


_virtualenv = 'tempAgent'
_activate_virtualenv = os.path.join(_virtualenv, 'bin', 'activate')
@task
def deploy(c, conf, temp_agent_root='/opt/temp_agent'):
    """
    Deploy the agent to a host

    Example:
        inv deploy --conf=conf/prod.json
    """
    with print_title("Packaging"):
        package_path = package(c)
    config = read_conf(conf)
    rc = connect_with_sudo(config)

    def copy_artifacts():
        # Do not delete the agent root so we can keep some state there. Note
        # however we'll delete the virtualenv
        rc.sudo(f'mkdir -p {temp_agent_root}')
        rc.sudo(f"chown -R {config['agent']['user']} {temp_agent_root}")
        rc.put(package_path, temp_agent_root)
        tasks_path = glob.glob(os.path.join(_script_dir, 'tasks.py'))[0]
        rc.put(tasks_path, temp_agent_root)
        temp_agent_conf_root = f"{temp_agent_root}/conf"
        rc.run(f"mkdir -p {temp_agent_conf_root}")
        rc.put(conf, temp_agent_conf_root)

    def setup_virtual_env():
        rc.run('pip3 install virtualenv')
        rc.run(f"rm -rf {_virtualenv}")
        # NOTE: using `--system-site-packages` to inherit the grovepi library
        # installed system wide
        rc.run(f"python3 -m virtualenv --system-site-packages {_virtualenv}")

    def update_agent():
        with rc.prefix(f". {_activate_virtualenv}"):
            rc.run(f"pip install {os.path.basename(package_path)}")

    with print_title("Stopping agent"):
        pass  # TODO, do not fail if not setup

    with print_title("Copying artifacts"):
        copy_artifacts()
    # cd not available in Fabric 2
    with rc.prefix(f"cd {temp_agent_root}"):
        with print_title("Setting up virtualenv"):
            setup_virtual_env()
        with print_title("Updating agent"):
            update_agent()

    with print_title("Running smoke test for deployment"):
        smoke_test_deployment(c, conf, temp_agent_root)

    with print_title("Start agent"):
        pass  # TODO, setup systemd if needed

@task
def smoke_test_deployment(c, conf, temp_agent_root='/opt/temp_agent'): # pylint: disable=unused-argument
    """
    Example:
        inv smoke-test-deployment --conf=conf/prod.json
    """
    config = read_conf(conf)
    rc = connect_with_sudo(config)
    with rc.prefix(f"cd {temp_agent_root}"):
        with rc.prefix(f". {_activate_virtualenv}"):
            rc.run("""python -c 'from tempd.agent import Dht11TempMeter; print(Dht11TempMeter("foo").measure())'""") # pylint: disable=line-too-long

@task
def launch_agent(c, conf): # pylint: disable=unused-argument
    """Launch agent and block while it measures. Use Control+C to stop
    the program

    Example:
        inv launch-agent --conf=conf/prod.json
    """
    main = Main(read_conf(conf))
    deamon = main.create_deamon()
    deamon.start()
    print("that's all")
