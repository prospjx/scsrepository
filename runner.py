import os
import signal
import sys
import time
import subprocess
from pathlib import Path
import uvicorn
from gateway import app

BASE_DIR = Path(__file__).resolve().parent

SERVICES = [
    {
        "name": "courseapi",
        "dir": str(BASE_DIR / "courseapi"),
        "cmd": [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8001"],
        "env": {"DATABASE_URL": f"sqlite:///{str(BASE_DIR / 'course.db').replace('\\', '/')}"}
    },
    {
        "name": "studentapi",
        "dir": str(BASE_DIR / "studentapi"),
        "cmd": [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8002"],
        "env": {"DATABASE_URL": f"sqlite:///{str(BASE_DIR / 'student.db').replace('\\', '/')}"}
    },
    {
        "name": "schedulerapi",
        "dir": str(BASE_DIR / "schedulerapi"),
        "cmd": [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"],
        "env": {
            "DATABASE_URL": f"sqlite:///{str(BASE_DIR / 'scheduler.db').replace('\\', '/')}",
            "COURSE_API_URL": "http://127.0.0.1:8001",
            "STUDENT_API_URL": "http://127.0.0.1:8002",
            "AI_ASSISTANT_API_URL": "http://127.0.0.1:8003"
        }
    },
    {
        "name": "ai-assistant-api",
        "dir": str(BASE_DIR / "ai-assistant-api"),
        "cmd": [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8003"],
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
    # Give child services time to bind ports and seed data
    time.sleep(3)

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
