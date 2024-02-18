# Monitoring meetup

## Prerequisites:
Install [Minikube](https://minikube.sigs.k8s.io/docs/start/) to bootstrap a local one node cluster.
Minikube comes with a built-in kubectl installation.
Install [Helm](https://helm.sh/docs/intro/install/) - a "package manager" for Kubernetes to install and manage Kubernetes extensions.
Helm uses a packaging format called charts. 
A chart is a collection of files that describe a related set of Kubernetes resources.
### Bootstrap a cluster
`minikube start -p monitoring-meetup`
Switch to a profile:
`minikube profile monitoring-meetup`

## Kube-prometheus-stack Helm chart
kube-prometheus-stack is a collection of Kubernetes manifests, 
Grafana dashboards, and Prometheus rules combined with documentation and scripts that provides
Kubernetes cluster monitoring with Prometheus using the Prometheus Operator.

Add repository to install kube-prometheus-stack chart from
`helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`
`helm search repo prometheus-community`

Create a namespace for monitoring
`kubectl create namespace monitoring`
Install the kps chart
`helm install prometheus-operator prometheus-community/kube-prometheus-stack -f helm-values/kps-values.yml \
-n monitoring --version 55.0.0`
Multivalue configuration - use `helm multivalues`

TODO: helm template --release-name <release name>

To access Prometheus UI, port-forward the service to localhost:
`kubectl port-forward --namespace monitoring svc/prometheus-operator-kube-p-prometheus 9090:9090`

pull model vs push (PushGateway)

## Prometheus TSDB
sample, time series, chunk, block, WAL

Chunks exist within blocks.
New samples are first written to a chunk in the head block.
When the head block fills up, a new block is created, and the old head block becomes persistent on disk.
Chunks within a block remain immutable, while new blocks can be added or removed as needed.

### Scrape config
TODO: 

## An application that exposes metrics
`kubectl apply -f apps/counter-app-deployment.yaml`
`kubectl apply -f apps/counter-app-service.yaml`
Forward connections from a local port to a port on the pod
`kubectl port-forward svc/counter-app 8080`

### Metrics format /metrics
`http://localhost:8080/metrics`
```text
# HELP http_requests_total The total number of HTTP requests.
# TYPE http_requests_total counter
http_requests_total{method="post",code="200"} 1027 1395066363000
http_requests_total{method="post",code="400"}    3 1395066363000
```

### TODO: how to setup exporter endpoint


### service monitor
### pod monitor

### Explain helm-values/kps-values.yml
The default KPS chart values can be found [here](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml)

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

promQL, counter (sum(rate))

kube-state-metrics

grafana config
`helm upgrade prometheus-operator prometheus-community/kube-prometheus-stack -f helm-values/kps-values.yml \
-n monitoring --version 55.0.0`

add an existing dashboard

create a custom dashboard

demonstrate how to add a dashboard


variable

## Useful links:
[kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
[kube-prometheus-stack values](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml)
