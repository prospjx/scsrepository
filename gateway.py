import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart Course Scheduler API Gateway",
    version="1.0.0",
    description="Unified API Gateway routing to SCS microservices.",
)

# Enable CORS for GitHub Pages, Vercel, or custom domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COURSE_API_URL = os.getenv("COURSE_API_URL", "http://127.0.0.1:8001")
STUDENT_API_URL = os.getenv("STUDENT_API_URL", "http://127.0.0.1:8002")
SCHEDULER_API_URL = os.getenv("SCHEDULER_API_URL", "http://127.0.0.1:8000")
AI_ASSISTANT_API_URL = os.getenv("AI_ASSISTANT_API_URL", "http://127.0.0.1:8003")

async def forward_request(target_url: str, request: Request, timeout: float = 30.0) -> Response:
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        rp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )
    return Response(
        content=rp.content,
        status_code=rp.status_code,
        media_type=rp.headers.get("content-type"),
    )

@app.get("/")
def root():
    return {
        "service": "Smart Course Scheduler API Gateway",
        "status": "online",
        "routes": [
            "/api/v1/courses",
            "/api/v1/students",
            "/api/v1/scheduler",
            "/api/v1/analyze",
            "/health",
            "/docs"
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# 1. Course Service Proxy
@app.api_route("/api/v1/courses{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_courses(request: Request, path: str):
    return await forward_request(f"{COURSE_API_URL}/api/v1/courses{path}", request)

# 2. Student Service Proxy
@app.api_route("/api/v1/students{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_students(request: Request, path: str):
    return await forward_request(f"{STUDENT_API_URL}/api/v1/students{path}", request)

# 3. Scheduler Service Proxy
@app.api_route("/api/v1/scheduler{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_scheduler(request: Request, path: str):
    return await forward_request(f"{SCHEDULER_API_URL}/api/v1/scheduler{path}", request, timeout=45.0)

# 4. AI Assistant Service Proxy
@app.api_route("/api/v1/analyze{path:path}", methods=["GET", "POST"])
async def route_ai(request: Request, path: str):
    return await forward_request(f"{AI_ASSISTANT_API_URL}/api/v1/analyze{path}", request, timeout=90.0)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("gateway:app", host="0.0.0.0", port=port, reload=True)

