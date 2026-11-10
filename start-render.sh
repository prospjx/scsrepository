#!/bin/bash
set -e

echo "Starting Course API on 8001..."
cd /app/courseapi
DATABASE_URL="sqlite:////app/course.db" python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 &

echo "Starting Student API on 8002..."
cd /app/studentapi
DATABASE_URL="sqlite:////app/student.db" python -m uvicorn src.main:app --host 127.0.0.1 --port 8002 &

echo "Starting Scheduler API on 8000..."
cd /app/schedulerapi
DATABASE_URL="sqlite:////app/scheduler.db" \
COURSE_API_URL="http://127.0.0.1:8001" \
STUDENT_API_URL="http://127.0.0.1:8002" \
AI_ASSISTANT_API_URL="http://127.0.0.1:8003" \
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 &

echo "Starting AI Assistant API on 8003..."
cd /app/ai-assistant-api
python -m uvicorn src.main:app --host 127.0.0.1 --port 8003 &

# Wait a moment for background services to initialize
sleep 3

echo "Starting Gateway on ${PORT:-8080}..."
cd /app
exec python gateway.py
