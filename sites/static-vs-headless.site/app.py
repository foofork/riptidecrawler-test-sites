"""
Static vs Headless Test Site
Port: 5003
Tests static vs JavaScript-required content rendering
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from faker import Faker
import random

app = FastAPI(title="Static vs Headless Site")
templates = Jinja2Templates(directory="templates")

fake = Faker()
Faker.seed(42)
random.seed(42)

# Generate test data
articles = [
    {
        "id": i,
        "title": fake.catch_phrase(),
        "content": fake.text(300),
        "author": fake.name(),
        "date": fake.date_this_year().strftime("%Y-%m-%d")
    }
    for i in range(20)
]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with test overview"""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Static vs Headless Test Site"
    })


@app.get("/static/{article_id}", response_class=HTMLResponse)
async def static_page(request: Request, article_id: int):
    """75% - Static HTML, no JavaScript required"""
    if article_id >= len(articles):
        article_id = 0

    return templates.TemplateResponse("static.html", {
        "request": request,
        "article": articles[article_id],
        "requires_js": False
    })


@app.get("/dynamic/{article_id}", response_class=HTMLResponse)
async def dynamic_page(request: Request, article_id: int):
    """25% - Requires JavaScript rendering"""
    if article_id >= len(articles):
        article_id = 0

    return templates.TemplateResponse("dynamic.html", {
        "request": request,
        "article_id": article_id,
        "requires_js": True
    })


@app.get("/api/article/{article_id}")
async def api_article(article_id: int):
    """API endpoint for JavaScript-rendered content"""
    if article_id >= len(articles):
        article_id = 0
    return articles[article_id]


@app.get("/anti-bot-check", response_class=HTMLResponse)
async def anti_bot_check(request: Request):
    """Page that detects headless browsers"""
    return templates.TemplateResponse("anti_bot.html", {
        "request": request
    })


@app.get("/api/bot-check")
async def bot_check_result(user_agent: str = "", webdriver: str = ""):
    """API endpoint for bot detection results"""
    is_bot = webdriver.lower() == "true" or "headless" in user_agent.lower()
    return {
        "is_bot": is_bot,
        "user_agent": user_agent,
        "webdriver_detected": webdriver.lower() == "true",
        "recommendation": "Use stealth mode" if is_bot else "Normal browser detected"
    }


@app.get("/routing-logic")
async def routing_logic():
    """Return intelligent routing recommendations"""
    return {
        "static_pages": 15,
        "dynamic_pages": 5,
        "total_pages": 20,
        "static_percentage": 0.75,
        "dynamic_percentage": 0.25,
        "recommendation": "Route to static parser for 75% of pages, headless browser for 25%",
        "detection_method": "Check for 'data-requires-js' attribute in HTML"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
