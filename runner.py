import asyncio
import os
import signal
import sys
import subprocess
import uvicorn
from gateway import app

SERVICES = [
    {
        "name": "courseapi",
        "dir": "/app/courseapi",
        "cmd": ["python", "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8001"],
        "env": {"DATABASE_URL": "sqlite:////app/course.db"}
    },
    {
        "name": "studentapi",
        "dir": "/app/studentapi",
        "cmd": ["python", "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8002"],
        "env": {"DATABASE_URL": "sqlite:////app/student.db"}
    },
    {
        "name": "schedulerapi",
        "dir": "/app/schedulerapi",
        "cmd": ["python", "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"],
        "env": {
            "DATABASE_URL": "sqlite:////app/scheduler.db",
            "COURSE_API_URL": "http://127.0.0.1:8001",
            "STUDENT_API_URL": "http://127.0.0.1:8002",
            "AI_ASSISTANT_API_URL": "http://127.0.0.1:8003"
        }
    },
    {
        "name": "ai-assistant-api",
        "dir": "/app/ai-assistant-api",
        "cmd": ["python", "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8003"],
        "env": {}
    }
]

processes = []

def start_services():
    for s in SERVICES:
        env = os.environ.copy()
        env.update(s["env"])
        print(f"Starting {s['name']} in {s['dir']}...")
        p = subprocess.Popen(s["cmd"], cwd=s["dir"], env=env)
        processes.append((s["name"], p))

def cleanup(*args):
    print("Shutting down microservices...")
    for name, p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    start_services()

    port = int(os.environ.get("PORT", 8080))
    print(f"Starting unified Gateway on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
