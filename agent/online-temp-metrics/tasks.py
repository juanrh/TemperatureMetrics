"""
Python Invoke tasks for build commands
"""
import os
from contextlib import contextmanager

from invoke import task
from fabric import Config, Connection

_script_dir = os.path.dirname(__file__)
_build_dir = os.path.join(_script_dir, 'build')
_cross_build_dir = os.path.join(_script_dir, 'cross_build')
_cross_binary = os.path.join(_cross_build_dir, 'bin', 'main')

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
def build(c):
    """Build the code for this architecture"""
    with print_title("Building code"):
        c.run(f"mkdir -p {_build_dir}")
        with c.cd(_build_dir):
            c.run('cmake .. -GNinja')
            c.run('ninja')


@task
def cross_build(c):
    """Build the code for RPI 3B+"""
    with print_title("Building code for RPI 3B+"):
        cross_build_shell(c, cmd='project/ci/do_cross_build.sh')

@task
def cross_build_shell(c, cmd=''):
    """Open a shell on a container for cross build"""
    c.run(f"mkdir -p {_cross_build_dir}")
    bash_args = '' if len(cmd) == 0 else f"-c '{cmd}'"
    # `pty=True` for https://www.pyinvoke.org/faq.html#why-do-i-sometimes-see-err-stdin-is-not-a-tty
    c.run(f"docker run -it -v{_script_dir}:/home/conan/project --rm conanio/gcc7-armv7 /bin/bash {bash_args}", pty=True)

@task
def smoke_test(c, host):
    """Run a measurement on a RPI 3B+
    Examples:

    - inv smoke-test temp-comedor
    - inv smoke-test --host temp-comedor
    """
    rc = Connection(host)
    print('Copying artifacts')
    rc.put(_cross_binary, '/home/pi')
    print('Running smoke test')
    rc.run(f'/home/pi/{os.path.basename(_cross_binary)}')

@task
def release(c):
    """Run all tests and all code analysis tools"""
    pass # TODO


# TODO doc in readme