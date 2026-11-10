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
    launcher = str(BASE_DIR / "start_service.py")
    for s in SERVICES:
        env = os.environ.copy()
        env.update(s["env"])
        log_file = open(f"/app/{s['name']}.log", "w", buffering=1)
        cmd = [
            sys.executable,
            launcher,
            s["app_dir"],
            s["port"]
        ]
        print(f"Starting {s['name']} on port {s['port']}...", flush=True)
        p = subprocess.Popen(cmd, cwd=s["app_dir"], env=env, stdout=log_file, stderr=subprocess.STDOUT)
        processes.append((s["name"], p, log_file))
    time.sleep(5)

def cleanup(*args):
    print("Shutting down microservices...", flush=True)
    for name, p, lf in processes:
        try:
            p.terminate()
            lf.close()
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
