import json
import urllib.request
import base64

log_dashboard = {
    "dashboard": {
        "title": "Application Logs",
        "uid": "application-logs",
        "tags": ["microservices", "logs", "loki"],
        "timezone": "browser",
        "refresh": "5s",
        "schemaVersion": 38,
        "templating": {
            "list": [
                {
                    "name": "app",
                    "type": "custom",
                    "label": "Service",
                    "query": "all, courseapi, studentapi, schedulerapi, ai-assistant-api",
                    "current": {
                        "text": "all",
                        "value": "all"
                    },
                    "options": [
                        {"text": "all", "value": "all", "selected": True},
                        {"text": "courseapi", "value": "courseapi", "selected": False},
                        {"text": "studentapi", "value": "studentapi", "selected": False},
                        {"text": "schedulerapi", "value": "schedulerapi", "selected": False},
                        {"text": "ai-assistant-api", "value": "ai-assistant-api", "selected": False}
                    ]
                }
            ]
        },
        "panels": [
            {
                "id": 1,
                "title": "Log Volume Over Time by Service",
                "type": "timeseries",
                "gridPos": {"x": 0, "y": 0, "w": 24, "h": 7},
                "datasource": {"type": "loki", "uid": "loki-datasource"},
                "targets": [
                    {
                        "expr": "sum by (app) (count_over_time({namespace=\"default\"}[1m]))",
                        "legendFormat": "{{app}}",
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 2,
                "title": "Live Application Logs Stream",
                "type": "logs",
                "gridPos": {"x": 0, "y": 7, "w": 24, "h": 17},
                "datasource": {"type": "loki", "uid": "loki-datasource"},
                "options": {
                    "showLabels": True,
                    "wrapLogMessage": True,
                    "enableLogDetails": True,
                    "sortOrder": "Descending"
                },
                "targets": [
                    {
                        "expr": '{namespace="default"} |~ "$app" or {namespace="default", app=~"$app"}',
                        "refId": "A"
                    }
                ]
            }
        ]
    },
    "overwrite": True
}

import os

grafana_base = os.getenv("GRAFANA_URL", "http://localhost:3000")
data = json.dumps(log_dashboard).encode("utf-8")
req = urllib.request.Request(
    f"{grafana_base}/api/dashboards/db",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.b64encode(b"admin:admin").decode("utf-8")
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"Created/Updated dashboard '{log_dashboard['dashboard']['title']}': status={res.get('status')}, url={res.get('url')}")
except Exception as e:
    print(f"Error creating dashboard: {e}")

