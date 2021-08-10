# Online temp metrics daemon

## Devel environment

```bash
mkdir -p build && cd build
cmake .. -GNinja
ninja
./main
```

or alternatively: `source ci/env.sh && build`.

### Cross compile for RPI 3B+ 

This is using armv7l (see more in ../../deploy/rpi/). We can follow [How to use Docker to create and cross-build C and C++ Conan packages](https://docs.conan.io/en/latest/howtos/run_conan_in_docker.html#docker-conan) to build on docker. We don't even need to pass a conan profile for RPI as in [this example](https://github.com/conan-io/training/tree/master/cross_build), because the default Conan profile is adjusted to use the right architecture, as seen in [the docs](https://docs.conan.io/en/latest/howtos/run_conan_in_docker.html#using-the-images-to-cross-build-packages), and as visible in `~/.conan/profiles/default`. We also follow [Running and deploying packages](https://docs.conan.io/en/latest/devtools/running_packages.html) to deploy the cross compiled artifacts to `cross_build`.

Build with `source ci/env.sh && cross_build`. The binary is available at `cross_build/bin/main`, smoke test as follows:

```bash
TARGET_HOST=your host
scp cross_build/bin/main ${TARGET_HOST}:/home/pi
ssh ${TARGET_HOST} /home/pi/main
```

See also [Deployment challenges](https://docs.conan.io/en/latest/devtools/running_packages.html#deployment-challenges) for how to deal with issues with different versions of the C or C++ standard library.