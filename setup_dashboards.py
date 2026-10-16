import json
import urllib.request
import base64

dashboards = [
    {
        "dashboard": {
            "title": "API Latency",
            "uid": "api-latency",
            "tags": ["microservices", "latency", "api"],
            "timezone": "browser",
            "refresh": "10s",
            "schemaVersion": 38,
            "panels": [
                {
                    "id": 1,
                    "title": "P95 API Request Latency by Service & Handler",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 0, "w": 24, "h": 10},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "s",
                            "custom": {
                                "lineInterpolation": "smooth",
                                "spanNulls": True,
                            },
                        }
                    },
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service, handler))",
                            "legendFormat": "{{service}} - {{handler}} (p95)",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 2,
                    "title": "Average API Latency by Service",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 10, "w": 12, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "s",
                            "custom": {"lineInterpolation": "smooth"},
                        }
                    },
                    "targets": [
                        {
                            "expr": "sum(rate(http_request_duration_seconds_sum[5m])) by (service) / sum(rate(http_request_duration_seconds_count[5m])) by (service)",
                            "legendFormat": "{{service}} (avg)",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "P99 API Latency by Service",
                    "type": "timeseries",
                    "gridPos": {"x": 12, "y": 10, "w": 12, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "s",
                            "custom": {"lineInterpolation": "smooth"},
                        }
                    },
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))",
                            "legendFormat": "{{service}} (p99)",
                            "refId": "A",
                        }
                    ],
                },
            ],
        },
        "overwrite": True,
    },
    {
        "dashboard": {
            "title": "Error Rate",
            "uid": "error-rate",
            "tags": ["microservices", "errors"],
            "timezone": "browser",
            "refresh": "10s",
            "schemaVersion": 38,
            "panels": [
                {
                    "id": 1,
                    "title": "HTTP Error Rate Percentage (4xx/5xx)",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 0, "w": 24, "h": 10},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percentunit",
                            "custom": {"lineInterpolation": "smooth"},
                        }
                    },
                    "targets": [
                        {
                            "expr": 'sum(rate(http_requests_total{status=~"[45].."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service)',
                            "legendFormat": "{{service}} Error %",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 2,
                    "title": "Total HTTP Requests by Status Code",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 10, "w": 12, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "targets": [
                        {
                            "expr": "sum(rate(http_requests_total[5m])) by (service, status)",
                            "legendFormat": "{{service}} [{{status}}]",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "Failed Requests Rate (rps)",
                    "type": "stat",
                    "gridPos": {"x": 12, "y": 10, "w": 12, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "targets": [
                        {
                            "expr": 'sum(rate(http_requests_total{status=~"[45].."}[5m])) by (service)',
                            "legendFormat": "{{service}}",
                            "refId": "A",
                        }
                    ],
                },
            ],
        },
        "overwrite": True,
    },
    {
        "dashboard": {
            "title": "Pod Health",
            "uid": "pod-health",
            "tags": ["kubernetes", "health", "pods"],
            "timezone": "browser",
            "refresh": "10s",
            "schemaVersion": 38,
            "panels": [
                {
                    "id": 1,
                    "title": "Pod Status Phase (Running = 1, Down = 0)",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 0, "w": 24, "h": 6},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {
                                    "type": "value",
                                    "options": {
                                        "1": {"text": "Running", "color": "green"},
                                        "0": {"text": "Down", "color": "red"},
                                    },
                                }
                            ]
                        }
                    },
                    "targets": [
                        {
                            "expr": 'sum by (pod) (kube_pod_status_phase{namespace="default", phase="Running"})',
                            "legendFormat": "{{pod}}",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 2,
                    "title": "Container Restarts (Total)",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 6, "w": 12, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "targets": [
                        {
                            "expr": 'sum by (pod) (kube_pod_container_status_restarts_total{namespace="default"})',
                            "legendFormat": "{{pod}}",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "Pod Readiness",
                    "type": "timeseries",
                    "gridPos": {"x": 12, "y": 6, "w": 12, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "max": 1,
                            "min": 0,
                        }
                    },
                    "targets": [
                        {
                            "expr": 'sum by (pod) (kube_pod_status_ready{condition="true", namespace="default"})',
                            "legendFormat": "{{pod}} (Ready)",
                            "refId": "A",
                        }
                    ],
                },
            ],
        },
        "overwrite": True,
    },
    {
        "dashboard": {
            "title": "Resource Usage",
            "uid": "resource-usage",
            "tags": ["kubernetes", "resources", "cpu", "memory"],
            "timezone": "browser",
            "refresh": "10s",
            "schemaVersion": 38,
            "panels": [
                {
                    "id": 1,
                    "title": "Container CPU Usage (cores)",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 0, "w": 12, "h": 9},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "none",
                            "custom": {"lineInterpolation": "smooth"},
                        }
                    },
                    "targets": [
                        {
                            "expr": 'sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="default", container!=""}[5m]))',
                            "legendFormat": "{{pod}}",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 2,
                    "title": "Container Memory Usage (Working Set)",
                    "type": "timeseries",
                    "gridPos": {"x": 12, "y": 0, "w": 12, "h": 9},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "bytes",
                            "custom": {"lineInterpolation": "smooth"},
                        }
                    },
                    "targets": [
                        {
                            "expr": 'sum by (pod) (container_memory_working_set_bytes{namespace="default", container!=""})',
                            "legendFormat": "{{pod}}",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "Top Pods by Memory Consumption",
                    "type": "barGauge",
                    "gridPos": {"x": 0, "y": 9, "w": 24, "h": 8},
                    "datasource": {"type": "prometheus", "uid": "PBFA97CFB590B2093"},
                    "fieldConfig": {
                        "defaults": {
                            "unit": "bytes",
                        }
                    },
                    "targets": [
                        {
                            "expr": 'topk(10, sum by (pod) (container_memory_working_set_bytes{namespace="default", container!=""}))',
                            "legendFormat": "{{pod}}",
                            "refId": "A",
                        }
                    ],
                },
            ],
        },
        "overwrite": True,
    },
]

import os

grafana_base = os.getenv("GRAFANA_URL", "http://localhost:3000")
for db in dashboards:
    data = json.dumps(db).encode("utf-8")
    req = urllib.request.Request(
        f"{grafana_base}/api/dashboards/db",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Basic " + base64.b64encode(b"admin:admin").decode("utf-8"),
        },
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"Created/Updated dashboard '{db['dashboard']['title']}': status={res.get('status')}, url={res.get('url')}")

