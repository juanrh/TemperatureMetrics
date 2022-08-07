# k8s deployment with Prometheus

Assuming a k8s cluster is already setup

## Prometheus initial setup

Goal: setup Prometheus server, Alert manager, and Grafana 

Using [Prometheus Operator](https://prometheus-operator.dev/).  

The [Prometheus Operator quick start](https://prometheus-operator.dev/docs/prologue/quick-start/#deploy-kube-prometheus) suggests using the manifests in [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus) that first deploy the CRDs for Prometheus operator (in `manifests/setup`), and then manifest (in `manifests`) to instantiate both Prometheus Operator CRs and other resources to get a starting point for a monitoring infra in a k8s cluster. That setup makes sense for production HA deployment, but not for my RPI based k3s cluster, as it has too many replicas of Prometheus and additional components like the blackbox exporter and prometheus adapter for exposing k8s metrics in prometheus for the horizontal pod autoscaler.


Following [Customizing Kube-Prometheus](https://github.com/prometheus-operator/kube-prometheus/blob/main/docs/customizing.md) and adapting the scripts and ideas there, we get a [jsonnet](https://jsonnet.org/)-based setup to reuse the manifests in kube-prometheus, that in turn install and configure the CRs from prometheus-operator. This works as follows from folder `kube-prometheus`:

- `jsonnetfile.json` declares a jsonnet dependency to "https://github.com/prometheus-operator/kube-prometheus.git". With `make jsonnet/deps` we use `jb` (jsonnet-bundler) to download all our jsonnet dependencies to the gitignored folder `vendor`.
- `main.jsonnet` is the entry point for the jsonnet configuration for our project, that imports `kube-prometheus` and customizes it for our project. With `make jsonnet/build` we run `jsonnet` to render it to JSON k8s manifests, and to convert those to YAML into the gitignored folder `manifests`
  - For example, comment `{ ['blackbox-exporter-' + name]:` to disable generating manifests for blackbox exporter. As a result the files `manifests/blackbox-exporter-*` are not rendered.
  - `jsonnet/build` depends on `jsonnet/deps`, and it's called by the default target `default`
- To deploy the manifests first use `make deploy/operator` to install the operator, and after waiting some time use `make deploy/monitoring-stack` to deploy the prometheus-operator specific CRs. 

So the basic usage is:

```bash
cd kube-prometheus
# render manifests
make

# only first time, installs operator
make deploy/operator
# each time the CR configs change
make deploy/monitoring-stack

# enable the web UIs
make ui/prometheus/start
make ui/alertmanager/start
make ui/grafana/start
# disable port forwarding for UIs
make ui/prometheus/stop
make ui/alertmanager/stop
make ui/grafana/stop
```

## Prometheus configuration for the temperature agent

Goal:

- setup target for a temp agent
- setup grafana dashboard for metrics
- setup alert with email notification
