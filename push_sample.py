import json
import time
import urllib.request

now_ns = str(time.time_ns())
payload = {
    "streams": [
        {
            "stream": {"app": "courseapi", "namespace": "default"},
            "values": [[now_ns, 'INFO: 10.0.1.173:39842 - "GET /api/v1/courses HTTP/1.1" 200 OK']]
        },
        {
            "stream": {"app": "studentapi", "namespace": "default"},
            "values": [[now_ns, 'INFO: 10.0.2.148:42138 - "GET /health HTTP/1.1" 200 OK']]
        },
        {
            "stream": {"app": "schedulerapi", "namespace": "default"},
            "values": [[now_ns, 'INFO: 10.0.1.113:50124 - "GET /health HTTP/1.1" 200 OK']]
        },
        {
            "stream": {"app": "ai-assistant-api", "namespace": "default"},
            "values": [[now_ns, 'INFO: 10.0.1.173:36132 - "GET /health HTTP/1.1" 200 OK']]
        }
    ]
}
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request("http://localhost:3100/loki/api/v1/push", data=data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("Pushed status:", resp.status)
except Exception as e:
    print("Error:", e)
