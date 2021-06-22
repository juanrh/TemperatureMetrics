#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

pushd ${SCRIPT_DIR}/..
mypy --config-file "${SCRIPT_DIR}/mypy.ini" main.py tempd
popd
