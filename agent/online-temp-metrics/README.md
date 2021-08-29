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

    analyze                  Run all static analysis tools
    build                    Build the code for this architecture
    ci-build                 Run the CI build locally in a Docker container
    ci-build-image-publish   Publish the build image to DockerHub, so it is available
    ci-build-shell           Open a shell in a container for CI builds
    cross-build              Build the code for RPI 3B+
    cross-build-shell        Open a shell on a container for cross build
    release                  Build, run all tests and all static analysis tools
    smoke-test               Run a measurement on a RPI 3B+
  ```

### Cross compile for RPI 3B+ 

This is using armv7l (see more in ../../deploy/rpi/). We can follow [How to use Docker to create and cross-build C and C++ Conan packages](https://docs.conan.io/en/latest/howtos/run_conan_in_docker.html#docker-conan) to build on docker. We don't even need to pass a conan profile for RPI as in [this example](https://github.com/conan-io/training/tree/master/cross_build), because the default Conan profile is adjusted to use the right architecture, as seen in [the docs](https://docs.conan.io/en/latest/howtos/run_conan_in_docker.html#using-the-images-to-cross-build-packages), and as visible in `~/.conan/profiles/default`. We also follow [Running and deploying packages](https://docs.conan.io/en/latest/devtools/running_packages.html) to deploy the cross compiled artifacts to `cross_build`.

Build with the Invoke task `cross-build` seen above. The binary is available at `cross_build/bin/main`, use the `smoke-test` task for basic smoke testing.

See also [Deployment challenges](https://docs.conan.io/en/latest/devtools/running_packages.html#deployment-challenges) for how to deal with issues with different versions of the C or C++ standard library.

### CI setup

Github actions it's quite difficult to use with docker (see [this](https://github.community/t/docker-action-cant-create-folder-in-runners-home-directory/17816/5), [this](https://stackoverflow.com/questions/57830375/github-actions-workflow-error-permission-denied), and [this](https://github.com/dockcross/dockcross/issues/231)). TravisCI it's trivial to setup with Docker, and Docker in Docker works easily to trigger cross compilation container from the main container

## Conclusions

Things that didn't work out well:

- Conan for dependencies: The vast majority of Conan packages don't support ARM, the answer I got in #conan at CppLang slack is that packages for this platform are not used. This means that using Conan altogether is probably not a good idea for this project, it solved cross compilation but there are simpler options (see below). So Conan it's not a long term solution, even just for cross compilation, because as don't publish packages for ARM they might as well deprecate the images for cross compilation at some point.
- Replacing cross compilation with native compilation with Docker+Qemu is not an option for Raspian: because [Docker images for Raspiban for raspberry pi are not maintained](https://www.raspberrypi.org/forums/viewtopic.php?t=280255), and in particular there is no image for Raspbian 10 (buster). This means doing native builds for RPI using emulation as [here](https://community.arm.com/developer/tools-software/tools/b/tools-software-ides-blog/posts/getting-started-with-docker-for-arm-on-linux) it's not an option. 
- This suggests RPI with Raspnian it's not a suitable platform suitable for native development with C++, although it's a simple option for languages running in virtual machines. Cross compilation is delicate, the [right floating point support](https://github.com/juanrh/TemperatureMetrics/commit/8dfb87596c74ba8511f873d5ccb08d810ec7c397) is required, and this is a very simple program, we could easily get into issues with glibc version or the sysroot. Some ideas for improving the situation:
  - use official RPI cross compilation toolchain, see e.g. [this](https://medium.com/@au42/the-useful-raspberrypi-cross-compile-guide-ea56054de187).
  - use other OS that has an image available: e.g. [Ubuntu Core](https://ubuntu.com/core/docs) or [Fedora IoT](https://getfedora.org/iot/).
  - other options are too complex:
    - crosstool-NG: no specific advantage compared to using the official toolchain
    - custom distro / image with yocto or buildroot: much complex than Fedora IoT or Ubuntu Core, probably lead to smaller and more optimized images, but that makes sense for longer projects and more constrained HW setups
  - use other languages: Python is really easy, but more high performance languages like Go or Rust migth be work exploring. Cross compiling Rust to work in AWS Lambda it's quite easy, [cross compilation in Go](https://golangcookbook.com/chapters/running/cross-compiling/) also looks easy, Go statically links the runtime to each binary which could eliminate libc version issues. Also, this languages have built-in package managers, so maybe they have ARM packages available. That allows using basic stuff like gRPC or high level http server frameworks, to build more sophisticated interactions between agents and server side code


_Next steps for future projects_: the most promising option seems

- For OS: use Fedora IoT or Ubuntu Core instead of Raspbian
- For compilating to target host: use a Docker container for ARM emulated with Qemu instead of cross compilation
- For dependencies: don't count on Conan, and instead build them into the build container, and consider even deploying the container. But also investigate Fedora Iot or Ubuntu Core, to see what is their recommended development workflow, that likely covers dependencies and cross compilation too, see e.g. [this](https://docs.fedoraproject.org/en-US/iot/build-docker/) 

### TODO

- connect with front
- tests with mocks: add coverage, run with valgrind or similar
  - also open close devices in C code
- code analysis: at least style, linter, asan, tsan, see https://github.com/analysis-tools-dev/static-analysis#cpp
  - https://github.com/google/sanitizers
    - https://clang.llvm.org/docs/ThreadSanitizer.htmls
  - https://clang.llvm.org/extra/clang-tidy/