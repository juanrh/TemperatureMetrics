# Some taken from https://github.com/prometheus-operator/kube-prometheus/blob/main/Makefile

MKFILE_PATH  := $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT_DIR := $(dir $(MKFILE_PATH))
TMP_DIR := $(ROOT_DIR)/tmp
BIN_DIR?=$(TMP_DIR)/bin
SCRIPTS_DIR?=$(ROOT_DIR)/scripts
JB_BIN=$(BIN_DIR)/jb
JSONNET_BIN=$(BIN_DIR)/jsonnet
GOJSONTOYAML_BIN=$(BIN_DIR)/gojsontoyaml
TOOLING=$(JB_BIN) $(GOJSONTOYAML_BIN) $(JSONNET_BIN)

default: jsonnet/build

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(TOOLING): $(BIN_DIR)
	echo Installing tools from scripts/tools.go
	cd $(SCRIPTS_DIR) && go mod tidy && cat tools.go | grep _ | awk -F'"' '{print $$2}' | xargs -tI % go build -modfile=go.mod -o $(BIN_DIR) %

tooling: $(TOOLING)

.PHONY: clean
clean:
	rm -rf vendor manifests

.PHONY: jsonnet/deps
jsonnet/deps: export PATH = $(BIN_DIR):$(shell printenv PATH)
jsonnet/deps: $(JB_BIN)
	jb install

-PHONY: jsonnet/build
jsonnet/build: export PATH = $(BIN_DIR):$(shell printenv PATH)
jsonnet/build: tooling jsonnet/deps
	$(SCRIPTS_DIR)/jsonnet-build.sh $(ROOT_DIR)/main.jsonnet

deploy/operator:
	echo 'Assuming KUBECONFIG is properly set (e.g. with k3s_kubeconfig_enable)'
	kubectl apply --server-side -f $(ROOT_DIR)/manifests/setup
	echo 'Now check namespace "monitoring" for new resources'

deploy/monitoring-stack:
	echo 'Assuming KUBECONFIG is properly set (e.g. with k3s_kubeconfig_enable)'
	kubectl apply -f $(ROOT_DIR)/manifests/
	echo 'Now check namespace "monitoring" for new resources'

# As in https://prometheus-operator.dev/docs/prologue/quick-start/#access-prometheus
PROMETHEUS_PROXY_PID_FILE := $(TMP_DIR)/PROMETHEUS_PROXY_PID_FILE
ui/prometheus/start:
	kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090 & echo $$! > $(PROMETHEUS_PROXY_PID_FILE)
	echo "UI available at http://localhost:9090/"

ui/prometheus/stop:
	kill $$(cat $(PROMETHEUS_PROXY_PID_FILE))

# As in https://prometheus-operator.dev/docs/prologue/quick-start
ALERTMANAGER_PROXY_PID_FILE := $(TMP_DIR)/ALERTMANAGER_PROXY_PID_FILE
ui/alertmanager/start:
	kubectl --namespace monitoring port-forward svc/alertmanager-main 9093 & echo $$! > $(ALERTMANAGER_PROXY_PID_FILE)
	echo "UI available at http://localhost:9093/"

ui/alertmanager/stop:
	kill $$(cat $(ALERTMANAGER_PROXY_PID_FILE))

# As in https://prometheus-operator.dev/docs/prologue/quick-start
GRAFANA_PROXY_PID_FILE := $(TMP_DIR)/GRAFANA_PROXY_PID_FILE
ui/grafana/start:
	kubectl --namespace monitoring port-forward svc/grafana 3000 & echo $$! > $(GRAFANA_PROXY_PID_FILE)
	echo "UI available at http://localhost:3000/"
	echo 'You can login with the username "admin" and password "admin"'

ui/grafana/stop:
	kill $$(cat $(GRAFANA_PROXY_PID_FILE))
