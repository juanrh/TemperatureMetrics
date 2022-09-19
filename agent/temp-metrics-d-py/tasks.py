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
import logging
import logging.handlers

from invoke import task
from envbash import load_envbash
from fabric import Config, Connection
from jinja2 import Template
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
            root_module = 'tempd'
            run_tests = \
                f"pytest -vv -o log_cli=true -o log_cli_level=debug -s --pyargs {root_module}"
            get_coverage = f"--cov={root_module} --cov-report html --cov-report term"
            c.run(f"{run_tests} {get_coverage}")

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

_service_file_template = Template('''
[Unit]
Description={{ service_name }}
After=network.target

[Service]
ExecStart={{ launch_cmd }}
WorkingDirectory={{ working_directory }}
StandardOutput=inherit
StandardError=inherit
Restart=always
User={{ user }}

[Install]
WantedBy=multi-user.target

''')
_virtualenv = 'tempAgent'
_activate_virtualenv = os.path.join(_virtualenv, 'bin', 'activate')
@task
def deploy(c, conf):
    """
    Deploy the agent to a host

    Example:
        inv deploy --conf=conf/prod.json
    """
    with print_title("Packaging"):
        package_path = package(c)
    config = read_conf(conf)
    rc = connect_with_sudo(config)
    temp_agent_root = config['deploy']['temp_agent_root']

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
        conf_root = os.path.dirname(conf)
        aws_credentials_file = os.path.join(conf_root, config['aws']['credentials_filename'])
        rc.put(aws_credentials_file, temp_agent_conf_root)
        rc.sudo(f"chmod 600 {temp_agent_conf_root}/*")

    def setup_virtual_env():
        rc.run('pip3 install virtualenv')
        rc.run(f"rm -rf {_virtualenv}")
        # NOTE: using `--system-site-packages` to inherit the grovepi library
        # installed system wide
        rc.run(f"python3 -m virtualenv --system-site-packages {_virtualenv}")

    def update_agent():
        with rc.prefix(f". {_activate_virtualenv}"):
            rc.run(f"pip install {os.path.basename(package_path)}")

    def setup_systemd():
        """https://www.raspberrypi.org/documentation/linux/usage/systemd.md"""
        service_name=config['deploy']['service_name']
        launch_cmd=f"/bin/bash -c 'source {_activate_virtualenv} && inv launch-agent --conf={conf}'"
        service_file_contents = _service_file_template.render(
            service_name=service_name,
            launch_cmd=launch_cmd,
            working_directory=temp_agent_root,
            user=config['agent']['user']
        )
        local_systemd_conf = os.path.join(_script_dir, 'build', service_name)
        with open(local_systemd_conf, 'w') as out_f:
            out_f.write(service_file_contents)
        rc.put(local_systemd_conf, temp_agent_root)
        systemd_conf = f"/etc/systemd/system/{service_name}.service"
        rc.sudo(f"cp {temp_agent_root}/{service_name} {systemd_conf}")
        rc.sudo('systemctl daemon-reload')
        rc.sudo(f"systemctl restart {service_name}.service")
        rc.sudo(f"systemctl status {service_name}.service")
        # Launch service at boot
        rc.sudo(f"systemctl enable {service_name}.service")

    with print_title("Copying artifacts"):
        copy_artifacts()
    # cd not available in Fabric 2
    with rc.prefix(f"cd {temp_agent_root}"):
        with print_title("Setting up virtualenv"):
            setup_virtual_env()
        with print_title("Updating agent"):
            update_agent()

    with print_title("(Re)Start agent"):
        setup_systemd()

def get_service_name(config):
    """Get the name of the systemctl service used for the agent"""
    service_name=config['deploy']['service_name']
    return f"{service_name}.service"

@task
def check_agent_status(c, conf):
    """
    Check status of the agent service

    Example:
        inv check-agent-status --conf=conf/prod.json
    """
    systemctl_agent(c, 'status', conf)

@task
def stop_agent(c, conf):
    """
    Stop the agent service

    Example:
        inv stop-agent --conf=conf/prod.json
    """
    systemctl_agent(c, 'stop', conf)
    check_agent_status(c, conf)

def systemctl_agent(c, command, conf): # pylint: disable=unused-argument
    """Run a systemctl command on the agent service"""
    config = read_conf(conf)
    rc = connect_with_sudo(config)
    service_name = get_service_name(config)
    return rc.sudo(f"systemctl {command} {service_name}")

def setup_logging(c, config, agent_root=None):
    """
    Setup logging

    Params:
    - config: a configuration dictionary
    - agent_root: path for the root directory or None.
    If not None logs will be stored in a "log" subdirectory
    of `agent_root`
    """
    loggging_conf = config['logging']
    logger = logging.getLogger()
    logger.setLevel(loggging_conf['level'])
    formatter = \
        logging.Formatter('%(asctime)s [%(levelname)s] - [%(process)d] - %(name)s: %(message)s')
    def setup_handler(handler):
        handler.setFormatter(formatter)
        handler.setLevel(loggging_conf['level'])
        logger.addHandler(handler)
    stdoutHandler = logging.StreamHandler()
    setup_handler(stdoutHandler)
    if agent_root is not None:
        logging_root = os.path.join(agent_root, 'log')
        c.run(f"mkdir -p {logging_root}")
        service_name=config['deploy']['service_name']
        log_filename = os.path.join(logging_root, f"{service_name}.log")
        rotating_handler = logging.handlers.TimedRotatingFileHandler(
            log_filename,
            when=loggging_conf['rotationIntervalUnit'],
            interval=loggging_conf['rotationInterval'],
            backupCount=loggging_conf['maxLogFiles']
        )
        setup_handler(rotating_handler)

@task
def launch_agent(c, conf): # pylint: disable=unused-argument
    """Launch agent and block while it measures. Use Control+C to stop
    the program

    Example:
        inv launch-agent --conf=conf/dev.json
        inv launch-agent --conf=conf/prod.json
    """
    config = read_conf(conf)
    conf_root = os.path.dirname(conf)
    agent_root = os.path.dirname(conf_root)
    aws_credentials_file = os.path.join(conf_root, config['aws']['credentials_filename'])
    load_envbash(aws_credentials_file)

    setup_logging(c, config, agent_root)
    Main(config).run()
