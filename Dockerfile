FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn httpx

# Copy microservice directories and the gateway entrypoint
COPY courseapi /app/courseapi
COPY studentapi /app/studentapi
COPY schedulerapi /app/schedulerapi
COPY ai-assistant-api /app/ai-assistant-api
COPY gateway.py /app/gateway.py

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "gateway.py"]
