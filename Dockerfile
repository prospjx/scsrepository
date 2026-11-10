FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-unified.txt .
RUN pip install --no-cache-dir -r requirements-unified.txt

# Copy all service modules and unified server
COPY courseapi /app/courseapi
COPY studentapi /app/studentapi
COPY schedulerapi /app/schedulerapi
COPY ai-assistant-api /app/ai-assistant-api
COPY unified_server.py /app/

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "unified_server.py"]

