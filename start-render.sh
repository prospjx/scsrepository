#!/bin/bash
set -e

echo "Starting Course API on 8001..."
cd /app/courseapi
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 &

echo "Starting Student API on 8002..."
cd /app/studentapi
python -m uvicorn src.main:app --host 127.0.0.1 --port 8002 &

echo "Starting Scheduler API on 8000..."
cd /app/schedulerapi
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 &

echo "Starting AI Assistant API on 8003..."
cd /app/ai-assistant-api
python -m uvicorn src.main:app --host 127.0.0.1 --port 8003 &

echo "Starting Gateway on ${PORT:-8080}..."
cd /app
exec python gateway.py

