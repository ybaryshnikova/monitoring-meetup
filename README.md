# Monitoring meetup

## Prerequisites:
Install [Minikube](https://minikube.sigs.k8s.io/docs/start/) to bootstrap a local one node cluster.
Minikube comes with a built-in kubectl installation.
Install [Helm](https://helm.sh/docs/intro/install/) - a "package manager" for Kubernetes to install and manage Kubernetes extensions.
Helm uses a packaging format called charts. 
A chart is a collection of files that describe a related set of Kubernetes resources.
## Bootstrap a cluster
`minikube start -p monitoring-meetup`
Switch to a profile:
`minikube profile monitoring-meetup`

## Kube-prometheus-stack Helm chart
kube-prometheus-stack is a collection of Kubernetes manifests, 
Grafana dashboards, and Prometheus rules combined with documentation and scripts that provides
Kubernetes cluster monitoring with Prometheus using the Prometheus Operator.
- Prometheus Operator
- Grafana
- AlertManager

Resource is an object managed by Kubernetes (pod, namespace, deployment, service, etc.).
Custom resources are objects that are not part of the Kubernetes core API, but are instead defined by the user.

Add repository to install kube-prometheus-stack chart from
```commandline
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm search repo prometheus-community
```

Create a namespace for monitoring
```commandline
kubectl create namespace monitoring
```
Install the kps chart
```commandline
helm install prometheus-operator prometheus-community/kube-prometheus-stack -f helm-values/kps-values.yml \
-n monitoring --version 55.0.0
```
Multivalue configuration - use `helm multivalues`

To access Prometheus UI, port-forward the service to localhost:
```commandline
kubectl port-forward --namespace monitoring svc/prometheus-operator-kube-p-prometheus 9090:9090
```

pull model vs push (PushGateway)

## Prometheus 
### Prometheus TSDB
sample, time series, chunk, block, WAL

Chunks exist within blocks.
New samples are first written to a chunk in the head block.
When the head block fills up, a new block is created, and the old head block becomes persistent on disk.
Chunks within a block remain immutable, while new blocks can be added or removed as needed.

### An application that exposes metrics
```commandline
kubectl apply -f apps/counter-app-deployment.yaml
kubectl apply -f apps/counter-app-service.yaml
```
Forward connections from a local port to a port on the pod
```commandline
kubectl port-forward svc/counter-app 8080
```

### Scrape config
Status -> Configuration
[Scrape config example](https://fabianlee.org/2022/07/08/prometheus-monitoring-services-using-additional-scrape-config-for-prometheus-operator/)
```commandline
kubectl get prometheus -n monitoring prometheus-operator-kube-p-prometheus -o yaml
```

### Metrics example app
```commandline
https://github.com/ybaryshnikova/prometheus-metrics-example
```

### Metrics format /metrics
```commandline
http://localhost:8080/metrics
```
```text
# HELP flask_exporter_info Multiprocess metric
# TYPE flask_exporter_info gauge
flask_exporter_info{pid="12",version="0.18.1"} 1.0
flask_exporter_info{pid="10",version="0.18.1"} 1.0
flask_exporter_info{pid="11",version="0.18.1"} 1.0
flask_exporter_info{pid="8",version="0.18.1"} 1.0
flask_exporter_info{pid="9",version="0.18.1"} 1.0
# HELP demo_app_button_clicks_total Multiprocess metric
# TYPE demo_app_button_clicks_total counter
demo_app_button_clicks_total 12.0
```

#### Exporters
An exporter is a piece of software that exposes metrics in a format that Prometheus can understand.
- [Flask Prometheus Exporter](https://pypi.org/project/prometheus-flask-exporter/)
- [Spring Boot Prometheus](https://medium.com/simform-engineering/revolutionize-monitoring-empowering-spring-boot-applications-with-prometheus-and-grafana-e99c5c7248cf)
- [Prometheus .NET](https://github.com/prometheus-net/prometheus-net)

### Service monitor
The Prometheus Operator includes a Custom Resource Definition that allows the definition of the ServiceMonitor. 
The ServiceMonitor is used to define an application you wish to scrape metrics from within Kubernetes, 
the controller will action the ServiceMonitors we define and automatically build the required Prometheus configuration.

`kubectl apply -f apps/monitors/counter-app-service-monitor.yaml`

### Explain helm-values/kps-values.yml
The default KPS chart values can be found [here](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml)
How config values are processed:
[prometheus.yaml](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/templates/prometheus/prometheus.yaml)

#### `serviceMonitorSelectorNilUsesHelmValues: false`
Do not set default values for serviceMonitorSelector if empty or nil.
```
{{- if .Values.prometheus.prometheusSpec.serviceMonitorSelector }}
  serviceMonitorSelector:
{{ tpl (toYaml .Values.prometheus.prometheusSpec.serviceMonitorSelector | indent 4) . }}
{{ else if .Values.prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues  }}
  serviceMonitorSelector:
    matchLabels:
      release: {{ $.Release.Name | quote }}
```
#### serviceMonitorSelector: {}, serviceMonitorNamespaceSelector: {}
Select all service monitors in all namespaces

#### ruleSelectorNilUsesHelmValues: false
Do not set default values for ruleSelector if it is empty or nil.
```
{{- if .Values.prometheus.prometheusSpec.ruleSelector }}
  ruleSelector:
{{ tpl (toYaml .Values.prometheus.prometheusSpec.ruleSelector | indent 4) . }}
{{ else if .Values.prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues  }}
  ruleSelector:
    matchLabels:
      release: {{ $.Release.Name | quote }}
```

troubleshooting (check targets, port configuration, service/pod monitor)
### Pod monitor
`kubectl apply -f apps/monitors/counter-app-pod-monitor.yaml`


### promQL
instant vector selectors, range vector selectors
`sum(rate(demo_app_button_clicks_total[2m])) by (pod)`

### Troubleshooting
`curl 'http://localhost:9090/api/v1/series?match[]=demo_app_button_clicks_total' | jq`
- Check Status -> Targets
- check helm values (serviceMonitorSelectorNilUsesHelmValues)
- check service monitor configuration

## Useful links:
[kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
[kube-prometheus-stack default config](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml)
[PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
Exporters:
[Flask Prometheus Exporter](https://pypi.org/project/prometheus-flask-exporter/)
[Spring Boot Prometheus](https://medium.com/simform-engineering/revolutionize-monitoring-empowering-spring-boot-applications-with-prometheus-and-grafana-e99c5c7248cf)
[Prometheus .NET](https://github.com/prometheus-net/prometheus-net)
