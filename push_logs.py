import subprocess
import time
import json
import urllib.request

PODS = [
    {"name": "courseapi", "cmd": ["kubectl", "logs", "-n", "default", "deploy/courseapi-deployment", "-f", "--tail=50"]},
    {"name": "studentapi", "cmd": ["kubectl", "logs", "-n", "default", "deploy/studentapi-deployment", "-f", "--tail=50"]},
    {"name": "schedulerapi", "cmd": ["kubectl", "logs", "-n", "default", "deploy/schedulerapi-deployment", "-f", "--tail=50"]},
    {"name": "ai-assistant-api", "cmd": ["kubectl", "logs", "-n", "default", "deploy/ai-assistant-api", "-f", "--tail=50"]},
]

LOKI_URL = "http://localhost:3100/loki/api/v1/push"

def push_log(app, line):
    ts = str(time.time_ns())
    payload = {
        "streams": [
            {
                "stream": {
                    "app": app,
                    "namespace": "default",
                    "job": "microservices"
                },
                "values": [
                    [ts, line.strip()]
                ]
            }
        ]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(LOKI_URL, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            pass
    except Exception as e:
        print(f"Error pushing log for {app}: {e}")

print("Starting log forwarder...")
for p in PODS:
    print(f"Checking initial logs for {p['name']}...")
    res = subprocess.run(["kubectl", "logs", "-n", "default", f"deploy/{p['name'] if p['name'] != 'courseapi' and p['name'] != 'studentapi' and p['name'] != 'schedulerapi' else p['name'] + '-deployment'}", "--tail=20"], capture_output=True, text=True)
    if res.stdout:
        for line in res.stdout.strip().splitlines():
            if line.strip():
                push_log(p["name"], line)
print("Initial logs forwarded to Loki.")
