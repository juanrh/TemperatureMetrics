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
_ci_dir = os.path.join(_script_dir, 'ci')
# This env var should only be set on containers, so we mount the correct
# host path when launching a new container from a container (docker in docker)
_source_code_env_var = 'ONLINE_TEMP_METRICS_SRC_DIR'
_source_code_dir = os.environ.get(_source_code_env_var, _script_dir)

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

def bash_args(cmd):
    return '' if len(cmd) == 0 else f"-c '{cmd}'"

@task
def cross_build_shell(c, cmd=''):
    """Open a shell on a container for cross build"""
    c.run(f"mkdir -p {_cross_build_dir}")
    # `pty=True` for https://www.pyinvoke.org/faq.html#why-do-i-sometimes-see-err-stdin-is-not-a-tty
    c.run(f"docker run -it -v{_source_code_dir}:/home/conan/project --rm conanio/gcc10-armv7hf /bin/bash {bash_args(cmd)}",
          pty=True)

@task
def ci_build(c):
    """Run the CI build locally in a Docker container
    
    NOTE: For CI to work we need to publish the image with
    with `inv ci-build-image-publish` after logging with
    `docker login`
    """
    c.run(f"rm -rf {_build_dir}")
    with print_title("Running CI build locally"):
        # Disable 'build/header_guard' on CI as it uses a different root path in the container
        ci_build_shell(c, cmd='inv release --extra-linter-options --filter=-build/header_guard')

_ci_build_image_name = 'online-temp-metrics-ci'
@task
def ci_build_shell(c, cmd=''):
    """Open a shell in a container for CI builds"""
    with c.cd(_ci_dir):
        c.run(f"docker build -t {_ci_build_image_name} .")
    c.run(f"""docker run -it \
  -e {_source_code_env_var}={_script_dir}\
  -v{_script_dir}:/home/conan/project \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --rm {_ci_build_image_name} /bin/bash {bash_args(cmd)}""",
          pty=True)

_ci_build_image_repo = f"juanrh/{_ci_build_image_name}"
@task
def ci_build_image_publish(c):
    """Publish the build image to DockerHub, so it is available
    to Github actions.
    This assumes the shell already logged with `docker login`"""
    # ensure the image is built
    ci_build_shell(c, 'ls')
    c.run(f"docker tag {_ci_build_image_name} {_ci_build_image_repo}")
    c.run(f"docker push {_ci_build_image_repo}")

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
def analyze(c, extra_linter_options=''):
    """Run all static analysis tools"""
    with print_title("Checking for style errors with cpplint"):
        # https://github.com/cpplint/cpplint
        # https://google.github.io/styleguide/cppguide.html#cpplint
        # See error descriptions in https://google.github.io/styleguide/cppguide.html
        print(f"extra_linter_options = [{extra_linter_options}]")
        c.run(f"""cpplint \
    --linelength=105 \
    --counting=detailed {extra_linter_options} \
    $(find src include -name *.h -or -name *.c -or -name *.cpp)""")
    with print_title("Running Cppcheck static code analyzer"):
        # http://cppcheck.sourceforge.net/
        c.run('cppcheck --check-config --enable=all --error-exitcode=1  --suppress=missingIncludeSystem -I include/ src/')
    with print_title("Running scan-build static code analyzer"):
        # https://clang-analyzer.llvm.org/scan-build.html
        scan_build_dir = 'scan_build_dir'
        c.run(f"rm -rf {scan_build_dir}")
        c.run(f"mkdir -p {scan_build_dir}")
        with c.cd(scan_build_dir):
            c.run('cmake ..')
            c.run('scan-build -o report -k make')

@task
def release(c, extra_linter_options=''):
    """Build, run all tests and all static analysis tools"""
    build(c)
    cross_build(c)
    analyze(c, extra_linter_options)
