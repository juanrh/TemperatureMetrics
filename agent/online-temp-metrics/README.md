# Online temp metrics daemon

## Devel environment

```bash
mkdir -p build && cd build
cmake .. -GNinja
ninja
./main
```

or alternatively use build scripts:

- One time setup:

  - Install pyevn and python 3.7.3: see [these instructions](../temp-metrics-d-py/README.md)
  - Create virtual env, and install dependencies

  ```bash
  pyenv shell 3.7.3
  pip install virtualenv
  # create virtualenv
  python -m virtualenv .venv
  # enter virtual env
  source .venv/bin/activate
  # install dependencies for build
  pip install -r ci/requirements.txt
  ```

- Daily usage:

  ```bash
  # activate env so we can use Invoke
  source .venv/bin/activate

  # list all available tasks
  $ inv -l
  Available tasks:

    analyze             Run all static analysis tools
    build               Build the code for this architecture
    cross-build         Build the code for RPI 3B+
    cross-build-shell   Open a shell on a container for cross build
    release             Build, run all tests and all static analysis tools
    smoke-test          Run a measurement on a RPI 3B+
  ```

### Cross compile for RPI 3B+ 

This is using armv7l (see more in ../../deploy/rpi/). We can follow [How to use Docker to create and cross-build C and C++ Conan packages](https://docs.conan.io/en/latest/howtos/run_conan_in_docker.html#docker-conan) to build on docker. We don't even need to pass a conan profile for RPI as in [this example](https://github.com/conan-io/training/tree/master/cross_build), because the default Conan profile is adjusted to use the right architecture, as seen in [the docs](https://docs.conan.io/en/latest/howtos/run_conan_in_docker.html#using-the-images-to-cross-build-packages), and as visible in `~/.conan/profiles/default`. We also follow [Running and deploying packages](https://docs.conan.io/en/latest/devtools/running_packages.html) to deploy the cross compiled artifacts to `cross_build`.

Build with the Invoke task `cross-build` seen above. The binary is available at `cross_build/bin/main`, use the `smoke-test` task for basic smoke testing.

See also [Deployment challenges](https://docs.conan.io/en/latest/devtools/running_packages.html#deployment-challenges) for how to deal with issues with different versions of the C or C++ standard library.

### CI setup

Github actions it's quite difficult to use with docker (see [this](https://github.community/t/docker-action-cant-create-folder-in-runners-home-directory/17816/5), [this](https://stackoverflow.com/questions/57830375/github-actions-workflow-error-permission-denied), and [this](https://github.com/dockcross/dockcross/issues/231)). TravisCI it's trivial to setup with Docker, and Docker in Docker works easily to trigger cross compilation container from the main container

### TODO

- Wrap in testeable class
- gRPC service: consider spsc Boost queue to communicate sensor and service
- connet with front
- tests with mocks: add coverage, run with valgrind or similar
- code analysis: at least style, linter, asan, tsan, see https://github.com/analysis-tools-dev/static-analysis#cpp
  - https://github.com/google/sanitizers
    - https://clang.llvm.org/docs/ThreadSanitizer.html
  - http://cppcheck.sourceforge.net/
  - https://clang.llvm.org/extra/clang-tidy/
