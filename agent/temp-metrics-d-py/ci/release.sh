#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function print_title {
    title="${1}"
    echo "${title}"
    echo '=========================='
}


pushd ${SCRIPT_DIR}/..
print_title "Checking types with mypy"
mypy --config-file "${SCRIPT_DIR}/mypy.ini" main.py tempd
echo
echo

print_title "Running pylint linter"
pylint main.py tempd
echo
echo

popd
