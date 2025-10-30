"""
Auth and Session Test Site
Port: 5008
Tests authentication, session management, and CSRF tokens
"""
from fastapi import FastAPI, Request, Response, Cookie, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="Auth and Session Site")
templates = Jinja2Templates(directory="templates")

# In-memory session store (use Redis in production)
sessions = {}
csrf_tokens = {}

# Test users (password is hashed with sha256)
USERS = {
    "admin": hashlib.sha256("password123".encode()).hexdigest(),
    "user": hashlib.sha256("test123".encode()).hexdigest(),
}


def create_session(username: str) -> str:
    """Create new session for user"""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "username": username,
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow()
    }
    return session_id


def create_csrf_token(session_id: str) -> str:
    """Create CSRF token for session"""
    token = secrets.token_urlsafe(32)
    csrf_tokens[session_id] = token
    return token


def verify_session(session_id: Optional[str]) -> Optional[dict]:
    """Verify session is valid and not expired"""
    if not session_id or session_id not in sessions:
        return None

    session = sessions[session_id]

    # Check if session expired (1 hour)
    if datetime.utcnow() - session["created_at"] > timedelta(hours=1):
        del sessions[session_id]
        return None

    # Update last accessed
    session["last_accessed"] = datetime.utcnow()
    return session


def verify_csrf(session_id: str, token: str) -> bool:
    """Verify CSRF token matches session"""
    return session_id in csrf_tokens and csrf_tokens[session_id] == token


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-and-session",
        "port": 5008,
        "uptime": "operational"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with login form"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if session:
        return RedirectResponse("/dashboard", status_code=302)

    csrf_token = create_csrf_token("pre-auth")

    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf_token": csrf_token
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """GET /login - Display login form"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if session:
        return RedirectResponse("/dashboard", status_code=302)

    csrf_token = create_csrf_token("pre-auth")

    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf_token": csrf_token
    })


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    response: Response = None
):
    """Handle login form submission"""
    # Verify CSRF token
    if not verify_csrf("pre-auth", csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # Verify credentials
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if username not in USERS or USERS[username] != password_hash:
        return templates.TemplateResponse("login.html", {
            "request": {},
            "error": "Invalid username or password",
            "csrf_token": create_csrf_token("pre-auth")
        })

    # Create session
    session_id = create_session(username)

    # Set session cookie
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=3600,
        samesite="lax"
    )

    return response


@app.api_route("/dashboard", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def dashboard(request: Request):
    """Protected dashboard requiring authentication"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if not session:
        return RedirectResponse("/login", status_code=302)

    csrf_token = create_csrf_token(session_id)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": session["username"],
        "session_created": session["created_at"].isoformat(),
        "csrf_token": csrf_token
    })


@app.api_route("/protected", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def protected_page(request: Request):
    """Protected page requiring authentication"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if not session:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse("protected.html", {
        "request": request,
        "username": session["username"],
        "message": "This is a protected page"
    })

@app.api_route("/profile", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def profile_page(request: Request):
    """Profile page requiring authentication"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if not session:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": session["username"]
    })

@app.api_route("/settings", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page requiring authentication"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if not session:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "username": session["username"]
    })

@app.get("/protected-data")
async def protected_data(request: Request):
    """API endpoint requiring authentication"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "message": "This is protected data",
        "username": session["username"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/logout")
async def logout(request: Request, csrf_token: str = Form(...)):
    """Handle logout"""
    session_id = request.cookies.get("session_id")

    if session_id:
        # Verify CSRF
        if not verify_csrf(session_id, csrf_token):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")

        # Delete session
        if session_id in sessions:
            del sessions[session_id]
        if session_id in csrf_tokens:
            del csrf_tokens[session_id]

    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session_id")
    return response


@app.get("/session-info")
async def session_info(request: Request):
    """Get current session information"""
    session_id = request.cookies.get("session_id")
    session = verify_session(session_id)

    if not session:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "username": session["username"],
        "session_id": session_id[:16] + "...",  # Partial for security
        "created_at": session["created_at"].isoformat(),
        "last_accessed": session["last_accessed"].isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5008)
