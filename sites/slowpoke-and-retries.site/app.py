"""
Slowpoke and Retries Test Site
Port: 5007
Tests timeout handling, rate limiting, and retry logic (inspired by httpbin.org)
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import asyncio
import time
from datetime import datetime, timedelta

app = FastAPI(title="Slowpoke and Retries Site")
templates = Jinja2Templates(directory="templates")

# Rate limiting state
rate_limit_state = {}
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW = 60  # seconds


def check_rate_limit(client_id: str) -> tuple[bool, int]:
    """Check if client has exceeded rate limit"""
    now = time.time()

    if client_id not in rate_limit_state:
        rate_limit_state[client_id] = []

    # Remove old requests outside window
    rate_limit_state[client_id] = [
        req_time for req_time in rate_limit_state[client_id]
        if now - req_time < RATE_LIMIT_WINDOW
    ]

    if len(rate_limit_state[client_id]) >= RATE_LIMIT_REQUESTS:
        oldest = rate_limit_state[client_id][0]
        retry_after = int(RATE_LIMIT_WINDOW - (now - oldest))
        return False, retry_after

    rate_limit_state[client_id].append(now)
    return True, 0


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "slowpoke-and-retries",
        "port": 5004,
        "uptime": "operational"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with test overview"""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Slowpoke and Retries Test Site"
    })


@app.get("/delay/{seconds}", response_class=JSONResponse)
async def delay_response(seconds: int, request: Request):
    """Delay response by N seconds (like httpbin.org/delay)"""
    if seconds > 60:
        return JSONResponse(
            {"error": "Maximum delay is 60 seconds"},
            status_code=400
        )

    start_time = time.time()
    await asyncio.sleep(seconds)
    elapsed = time.time() - start_time

    return {
        "url": str(request.url),
        "args": dict(request.query_params),
        "headers": dict(request.headers),
        "origin": request.client.host,
        "delay": seconds,
        "elapsed": round(elapsed, 3)
    }


@app.get("/rate-limited")
async def rate_limited_endpoint(request: Request):
    """Endpoint with rate limiting (5 requests per minute)"""
    client_id = request.client.host

    allowed, retry_after = check_rate_limit(client_id)

    if not allowed:
        return JSONResponse(
            {
                "error": "Rate limit exceeded",
                "message": f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds",
                "retry_after": retry_after
            },
            status_code=429,
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + retry_after))
            }
        )

    remaining = RATE_LIMIT_REQUESTS - len(rate_limit_state[client_id])

    return JSONResponse(
        {
            "success": True,
            "message": "Request accepted",
            "timestamp": datetime.utcnow().isoformat()
        },
        headers={
            "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time() + RATE_LIMIT_WINDOW))
        }
    )


@app.get("/unstable")
async def unstable_endpoint():
    """Randomly returns 200, 429, or 503 to test retry logic"""
    import random

    rand = random.random()

    if rand < 0.6:  # 60% success
        return {"success": True, "message": "Request successful"}
    elif rand < 0.8:  # 20% rate limit
        return JSONResponse(
            {"error": "Rate limit", "retry_after": 30},
            status_code=429,
            headers={"Retry-After": "30"}
        )
    else:  # 20% server error
        return JSONResponse(
            {"error": "Server temporarily unavailable"},
            status_code=503,
            headers={"Retry-After": "60"}
        )


@app.get("/timeout")
async def timeout_endpoint():
    """Endpoint that hangs for 60 seconds to test timeout handling"""
    await asyncio.sleep(60)
    return {"message": "If you see this, your timeout is > 60s"}


@app.get("/503-error")
async def server_error():
    """Always returns 503 with Retry-After header"""
    return JSONResponse(
        {"error": "Service temporarily unavailable", "retry_after": 120},
        status_code=503,
        headers={"Retry-After": "120"}
    )


@app.get("/retry-test")
async def retry_test(attempt: int = 1):
    """Succeeds on 3rd attempt, fails before that"""
    if attempt < 3:
        return JSONResponse(
            {"error": "Not ready yet", "attempt": attempt, "retry_after": 10},
            status_code=503,
            headers={"Retry-After": "10"}
        )

    return {"success": True, "message": "Success on attempt 3!", "attempt": attempt}


@app.get("/status/{code}")
async def custom_status(code: int):
    """Return any HTTP status code for testing"""
    messages = {
        200: "OK",
        201: "Created",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout"
    }

    message = messages.get(code, f"Status {code}")
    headers = {}

    if code == 429:
        headers["Retry-After"] = "60"
    elif code == 503:
        headers["Retry-After"] = "120"

    return JSONResponse(
        {"code": code, "message": message},
        status_code=code,
        headers=headers
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5007)
