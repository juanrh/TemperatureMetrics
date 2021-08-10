#!/usr/bin/env bash

PACKAGE_NAME='online_temp_metrics'
PACKAGE_VERSION='0.1'
PACKAGE_ORG='juanrh'
PACKAGE_CHANNEL='testing'

function build {
    mkdir -p build
    pushd build
    cmake .. -GNinja
    ninja
    popd
}

function cross_build {
    mkdir -p cross_build
    docker run -it -v$(pwd):/home/conan/project --rm conanio/gcc7-armv7 /bin/bash -c 'source project/ci/env.sh && do_cross_build'
}

function do_cross_build {
    # This should run on the container for
    # cross compilation
    conan create project "${PACKAGE_ORG}/${PACKAGE_CHANNEL}"
    # install leaves files here
    pushd project/cross_build
    conan install "${PACKAGE_NAME}/${PACKAGE_VERSION}@${PACKAGE_ORG}/${PACKAGE_CHANNEL}" -g virtualrunenv
    # We could use source activate_run.sh also here to have something
    # similar to a virtualenv, but running the binary fails because
    # we haven't enabled qemu
    popd
}
