#!/usr/bin/env bash

# Based on https://github.com/prometheus-operator/kube-prometheus/blob/main/build.sh

# This script uses arg $1 (name of *.jsonnet file to use) to generate the manifests/*.yaml files.

set -e -x -o pipefail

# Make sure to start with a clean 'manifests' dir
rm -rf manifests
mkdir -p manifests/setup

# Calling gojsontoyaml is optional, but we would like to generate yaml, not json
jsonnet -J vendor -m manifests "${1-example.jsonnet}" | xargs -I{} sh -c 'cat {} | gojsontoyaml > {}.yaml' -- {}

# Make sure to remove json files
find manifests -type f ! -name '*.yaml' -delete
rm -f kustomization
