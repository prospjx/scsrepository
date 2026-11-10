import os
import signal
import sys
import time
import subprocess
from pathlib import Path
import uvicorn
from gateway import app

BASE_DIR = Path(__file__).resolve().parent

course_db_path = (BASE_DIR / "course.db").as_posix()
student_db_path = (BASE_DIR / "student.db").as_posix()
scheduler_db_path = (BASE_DIR / "scheduler.db").as_posix()

SERVICES = [
    {
        "name": "courseapi",
        "app_dir": str(BASE_DIR / "courseapi"),
        "port": "8001",
        "env": {
            "DATABASE_URL": f"sqlite:///{course_db_path}",
        }
    },
    {
        "name": "studentapi",
        "app_dir": str(BASE_DIR / "studentapi"),
        "port": "8002",
        "env": {
            "DATABASE_URL": f"sqlite:///{student_db_path}",
        }
    },
    {
        "name": "schedulerapi",
        "app_dir": str(BASE_DIR / "schedulerapi"),
        "port": "8000",
        "env": {
            "DATABASE_URL": f"sqlite:///{scheduler_db_path}",
            "COURSE_API_URL": "http://127.0.0.1:8001",
            "STUDENT_API_URL": "http://127.0.0.1:8002",
            "AI_ASSISTANT_API_URL": "http://127.0.0.1:8003",
        }
    },
    {
        "name": "ai-assistant-api",
        "app_dir": str(BASE_DIR / "ai-assistant-api"),
        "port": "8003",
        "env": {}
    }
]

processes = []

def start_services():
    for s in SERVICES:
        env = os.environ.copy()
        env.update(s["env"])
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "--app-dir",
            s["app_dir"],
            "src.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            s["port"]
        ]
        print(f"Starting {s['name']} on port {s['port']} with --app-dir {s['app_dir']}...", flush=True)
        p = subprocess.Popen(cmd, cwd=s["app_dir"], env=env)
        processes.append((s["name"], p))
    time.sleep(4)

def cleanup(*args):
    print("Shutting down microservices...", flush=True)
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
    print(f"Starting unified Gateway on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
