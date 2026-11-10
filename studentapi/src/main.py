import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from src.database import Base, SessionLocal, engine
from src.routers import students
from src.seed import seed_db

Base.metadata.create_all(bind=engine)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "handler", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "handler"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed the database on startup with a mock student profile
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Student API",
    version="1.0.0",
    description="Manages student profiles and preferences.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception:
        status_code = "500"
        raise
    finally:
        duration = time.time() - start_time
        path = request.url.path
        REQUEST_COUNT.labels(
            method=request.method, handler=path, status=status_code
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, handler=path).observe(duration)
    return response


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(students.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
