FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install combined dependencies for all services
COPY requirements-unified.txt .
RUN pip install --no-cache-dir -r requirements-unified.txt

# Copy microservice directories and entrypoints
COPY courseapi /app/courseapi
COPY studentapi /app/studentapi
COPY schedulerapi /app/schedulerapi
COPY ai-assistant-api /app/ai-assistant-api
COPY gateway.py /app/gateway.py
COPY start-render.sh /app/start-render.sh

RUN dos2unix /app/start-render.sh && chmod +x /app/start-render.sh

# Environment variables for SQLite databases inside container
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL_COURSE="sqlite:////app/course.db"
ENV DATABASE_URL_STUDENT="sqlite:////app/student.db"
ENV DATABASE_URL_SCHEDULER="sqlite:////app/scheduler.db"
ENV COURSE_API_URL="http://127.0.0.1:8001"
ENV STUDENT_API_URL="http://127.0.0.1:8002"
ENV SCHEDULER_API_URL="http://127.0.0.1:8000"
ENV AI_ASSISTANT_API_URL="http://127.0.0.1:8003"

EXPOSE 8080

CMD ["/bin/bash", "/app/start-render.sh"]
