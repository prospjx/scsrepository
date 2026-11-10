FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
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
COPY runner.py /app/runner.py

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "runner.py"]
