"""
Common utilities for Invoke tasks
"""

from contextlib import contextmanager
from fabric import Config, Connection

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

def connect_with_sudo(config):
    """
    Connects to a remote host with sudo enabled
    """
    sudo_pass = config['agent']['sudo_pass']
    fabric_conf = Config(overrides={'sudo': {'password': sudo_pass}})
    return Connection(config['agent']['host'], config=fabric_conf)