from fastapi import FastAPI, Request, Response, HTTPException, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import time
from collections import defaultdict
import hashlib
import secrets

app = FastAPI()

# Rate limiting storage (in production, use Redis or similar)
rate_limit_store = defaultdict(lambda: {"count": 0, "window_start": time.time(), "burst_count": 0, "burst_start": time.time()})
session_store = {}

# Configuration
RATE_LIMIT_PER_MINUTE = 10
BURST_THRESHOLD = 5
BURST_WINDOW = 5  # seconds
SESSION_BYPASS = True  # Sessions bypass rate limits

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def check_rate_limit(ip: str) -> tuple[bool, str]:
    """Check if IP is within rate limits"""
    now = time.time()
    client_data = rate_limit_store[ip]

    # Check burst rate (5 requests in 5 seconds)
    if now - client_data["burst_start"] > BURST_WINDOW:
        client_data["burst_count"] = 0
        client_data["burst_start"] = now

    client_data["burst_count"] += 1

    if client_data["burst_count"] > BURST_THRESHOLD:
        return False, f"Burst limit exceeded: {client_data['burst_count']} requests in {BURST_WINDOW} seconds"

    # Check per-minute rate limit
    if now - client_data["window_start"] > 60:
        client_data["count"] = 0
        client_data["window_start"] = now

    client_data["count"] += 1

    if client_data["count"] > RATE_LIMIT_PER_MINUTE:
        return False, f"Rate limit exceeded: {client_data['count']} requests per minute"

    return True, "OK"

def validate_headers(request: Request) -> tuple[bool, str]:
    """Validate required headers"""
    accept_language = request.headers.get("Accept-Language")
    user_agent = request.headers.get("User-Agent")

    if not accept_language:
        return False, "Missing Accept-Language header"

    if not user_agent:
        return False, "Missing User-Agent header"

    return True, "OK"

def is_polite_crawler(user_agent: str) -> bool:
    """Detect polite crawlers"""
    polite_bots = [
        "googlebot", "bingbot", "slurp", "duckduckbot",
        "baiduspider", "yandexbot", "facebookexternalhit",
        "twitterbot", "linkedinbot", "applebot"
    ]
    user_agent_lower = user_agent.lower()
    return any(bot in user_agent_lower for bot in polite_bots)

def create_session(ip: str) -> str:
    """Create a new session"""
    session_id = hashlib.sha256(f"{ip}{secrets.token_hex(16)}{time.time()}".encode()).hexdigest()
    session_store[session_id] = {
        "ip": ip,
        "created": time.time(),
        "requests": 0
    }
    return session_id

def validate_session(session_id: Optional[str], ip: str) -> bool:
    """Validate session cookie"""
    if not session_id or session_id not in session_store:
        return False

    session = session_store[session_id]

    # Check if session is from same IP
    if session["ip"] != ip:
        return False

    # Check if session is expired (1 hour)
    if time.time() - session["created"] > 3600:
        del session_store[session_id]
        return False

    session["requests"] += 1
    return True

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware to enforce rate limiting and header validation"""

    # Skip rate limiting for static files and config endpoint
    if request.url.path in ["/favicon.ico", "/stats"]:
        return await call_next(request)

    ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")

    # Check for polite crawlers - allow with notice
    if is_polite_crawler(user_agent):
        response = await call_next(request)
        response.headers["X-Crawler-Detected"] = "polite-bot"
        return response

    # Check session cookie
    session_id = request.cookies.get("session_id")
    has_valid_session = validate_session(session_id, ip)

    if SESSION_BYPASS and has_valid_session:
        # Valid session bypasses rate limits
        response = await call_next(request)
        response.headers["X-Rate-Limit-Bypassed"] = "session"
        return response

    # Validate required headers
    headers_valid, header_msg = validate_headers(request)
    if not headers_valid:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "message": header_msg,
                "required_headers": ["Accept-Language", "User-Agent"]
            }
        )

    # Check rate limits
    allowed, limit_msg = check_rate_limit(ip)
    if not allowed:
        client_data = rate_limit_store[ip]
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": limit_msg,
                "retry_after": 60,
                "current_count": client_data["count"],
                "burst_count": client_data["burst_count"],
                "hint": "Create a session by visiting /create-session to bypass rate limits"
            },
            headers={
                "Retry-After": "60",
                "X-Rate-Limit-Limit": str(RATE_LIMIT_PER_MINUTE),
                "X-Rate-Limit-Remaining": str(max(0, RATE_LIMIT_PER_MINUTE - client_data["count"])),
                "X-Rate-Limit-Reset": str(int(client_data["window_start"] + 60))
            }
        )

    response = await call_next(request)

    # Add rate limit headers
    client_data = rate_limit_store[ip]
    response.headers["X-Rate-Limit-Limit"] = str(RATE_LIMIT_PER_MINUTE)
    response.headers["X-Rate-Limit-Remaining"] = str(max(0, RATE_LIMIT_PER_MINUTE - client_data["count"]))
    response.headers["X-Rate-Limit-Reset"] = str(int(client_data["window_start"] + 60))

    return response

@app.get("/", response_class=HTMLResponse)
async def index():
    """Index page explaining the anti-bot measures"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Anti-Bot Lite Test Site</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d32f2f; }
            .info-box { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; }
            .warning-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; }
            .success-box { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; }
            .rule { margin: 10px 0; padding: 10px; background: #fafafa; border-radius: 5px; }
            code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
            ul { line-height: 1.8; }
            a { color: #1976d2; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Anti-Bot Lite Test Site</h1>
            <p>This site implements basic anti-bot and rate limiting measures to test crawler behavior.</p>

            <div class="info-box">
                <h2>🔒 Protection Measures</h2>
                <div class="rule">
                    <strong>1. Rate Limiting:</strong> Maximum <code>10 requests per minute</code> per IP address
                </div>
                <div class="rule">
                    <strong>2. Burst Protection:</strong> Maximum <code>5 requests in 5 seconds</code> triggers instant 429
                </div>
                <div class="rule">
                    <strong>3. Required Headers:</strong>
                    <ul>
                        <li><code>Accept-Language</code> - Must be present</li>
                        <li><code>User-Agent</code> - Must be present</li>
                    </ul>
                </div>
                <div class="rule">
                    <strong>4. Session Bypass:</strong> Valid session cookies bypass rate limits
                </div>
                <div class="rule">
                    <strong>5. Polite Crawler Detection:</strong> Known good bots (Googlebot, etc.) are allowed
                </div>
            </div>

            <div class="warning-box">
                <h2>⚠️ What Triggers a 429 Response</h2>
                <ul>
                    <li>More than 10 requests per minute from single IP</li>
                    <li>More than 5 requests within 5 seconds (burst)</li>
                    <li>Missing <code>Accept-Language</code> header (400 error)</li>
                    <li>Missing <code>User-Agent</code> header (400 error)</li>
                </ul>
            </div>

            <div class="success-box">
                <h2>✅ How to Bypass Limits</h2>
                <ul>
                    <li><a href="/create-session">Create a session</a> - Sets a cookie that bypasses rate limits</li>
                    <li>Use a recognized crawler User-Agent (Googlebot, Bingbot, etc.)</li>
                    <li>Space out requests to stay under 10/minute</li>
                    <li>Respect the <code>Retry-After</code> header when you get a 429</li>
                </ul>
            </div>

            <h2>📊 Test Endpoints</h2>
            <ul>
                <li><a href="/page1">Page 1</a> - Regular content page</li>
                <li><a href="/page2">Page 2</a> - Another content page</li>
                <li><a href="/page3">Page 3</a> - More content</li>
                <li><a href="/create-session">Create Session</a> - Get a bypass cookie</li>
                <li><a href="/stats">View Stats</a> - See your rate limit status</li>
            </ul>

            <h2>🤖 Crawler Best Practices</h2>
            <p>Good crawlers should:</p>
            <ul>
                <li>Include proper <code>User-Agent</code> and <code>Accept-Language</code> headers</li>
                <li>Respect rate limits and <code>Retry-After</code> headers</li>
                <li>Handle 429 responses gracefully with exponential backoff</li>
                <li>Create sessions when offered to reduce server load</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/page1", response_class=HTMLResponse)
async def page1():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Page 1 - Anti-Bot Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #1976d2; }
        </style>
    </head>
    <body>
        <h1>📄 Page 1</h1>
        <p>This is a test page protected by rate limiting.</p>
        <p>You successfully made it past the anti-bot checks!</p>
        <p><a href="/">← Back to Home</a> | <a href="/page2">Next Page →</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/page2", response_class=HTMLResponse)
async def page2():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Page 2 - Anti-Bot Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #388e3c; }
        </style>
    </head>
    <body>
        <h1>📄 Page 2</h1>
        <p>Another test page with rate limiting protection.</p>
        <p>Still going strong! Your crawler is behaving well.</p>
        <p><a href="/page1">← Previous Page</a> | <a href="/page3">Next Page →</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/page3", response_class=HTMLResponse)
async def page3():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Page 3 - Anti-Bot Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #f57c00; }
        </style>
    </head>
    <body>
        <h1>📄 Page 3</h1>
        <p>The final test page in this sequence.</p>
        <p>Congratulations on respecting our rate limits!</p>
        <p><a href="/page2">← Previous Page</a> | <a href="/">Back to Home</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/create-session")
async def create_session_endpoint(request: Request):
    """Create a session cookie that bypasses rate limits"""
    ip = get_client_ip(request)
    session_id = create_session(ip)

    response = JSONResponse(
        content={
            "message": "Session created successfully",
            "session_id": session_id,
            "ip": ip,
            "benefits": [
                "Bypass rate limits",
                "Session valid for 1 hour",
                "Unlimited requests with valid session"
            ]
        }
    )

    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=3600,
        httponly=True,
        samesite="lax"
    )

    return response

@app.get("/stats")
async def stats(request: Request):
    """Show rate limit statistics for the client"""
    ip = get_client_ip(request)
    client_data = rate_limit_store[ip]
    session_id = request.cookies.get("session_id")
    has_session = validate_session(session_id, ip)

    now = time.time()
    window_remaining = max(0, 60 - (now - client_data["window_start"]))
    burst_remaining = max(0, BURST_WINDOW - (now - client_data["burst_start"]))

    return {
        "ip": ip,
        "has_valid_session": has_session,
        "rate_limit": {
            "limit": RATE_LIMIT_PER_MINUTE,
            "current_count": client_data["count"],
            "remaining": max(0, RATE_LIMIT_PER_MINUTE - client_data["count"]),
            "window_resets_in": f"{window_remaining:.1f}s"
        },
        "burst_protection": {
            "threshold": BURST_THRESHOLD,
            "current_count": client_data["burst_count"],
            "window_resets_in": f"{burst_remaining:.1f}s"
        },
        "active_sessions": len(session_store)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5011)
