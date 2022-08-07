//+build tools

// Adapted from https://github.com/prometheus-operator/kube-prometheus/blob/main/scripts/tools.go

// Package tools tracks dependencies for tools that used in the build process.
// See https://github.com/golang/go/wiki/Modules
package tools

import (
	_ "github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb"
	_ "github.com/brancz/gojsontoyaml"
	_ "github.com/google/go-jsonnet/cmd/jsonnet"
)