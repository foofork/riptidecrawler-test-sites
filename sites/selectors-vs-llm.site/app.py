"""
Selectors vs LLM Test Site
Port: 5002
Tests CSS selector reliability vs LLM extraction needs
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from faker import Faker
import random

app = FastAPI(title="Selectors vs LLM Site")
templates = Jinja2Templates(directory="templates")

# Seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)

# Generate test data
products = [fake.catch_phrase() for _ in range(20)]
prices = [round(random.uniform(10, 1000), 2) for _ in range(20)]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "selectors-vs-llm",
        "port": 5005,
        "uptime": "operational"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with site overview"""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Selectors vs LLM Test Site"
    })


@app.get("/clean", response_class=HTMLResponse)
async def clean_list(request: Request):
    """List of clean HTML pages"""
    return templates.TemplateResponse("list.html", {
        "request": request,
        "page_type": "clean",
        "items": list(range(len(products))),
        "title": "Clean HTML Pages"
    })


@app.get("/messy", response_class=HTMLResponse)
async def messy_list(request: Request):
    """List of messy HTML pages"""
    return templates.TemplateResponse("list.html", {
        "request": request,
        "page_type": "messy",
        "items": list(range(len(products))),
        "title": "Messy HTML Pages"
    })


@app.get("/products/clean/{item_id}", response_class=HTMLResponse)
async def products_clean_page(request: Request, item_id: int):
    """70% - Clean HTML with proper semantic tags and classes (products prefix)"""
    return await clean_page(request, item_id)


@app.get("/clean/{item_id}", response_class=HTMLResponse)
async def clean_page(request: Request, item_id: int):
    """70% - Clean HTML with proper semantic tags and classes"""
    if item_id >= len(products):
        item_id = 0

    return templates.TemplateResponse("clean.html", {
        "request": request,
        "item_id": item_id,
        "product": products[item_id],
        "price": prices[item_id],
        "description": fake.text(200),
        "rating": round(random.uniform(3.5, 5.0), 1),
        "reviews": random.randint(10, 500),
        "confidence": 0.95
    })


@app.get("/products/messy/{item_id}", response_class=HTMLResponse)
async def products_messy_page(request: Request, item_id: int):
    """30% - Messy HTML requiring LLM extraction (products prefix)"""
    return await messy_page(request, item_id)


@app.get("/messy/{item_id}", response_class=HTMLResponse)
async def messy_page(request: Request, item_id: int):
    """30% - Messy HTML requiring LLM extraction"""
    if item_id >= len(products):
        item_id = 0

    return templates.TemplateResponse("messy.html", {
        "request": request,
        "item_id": item_id,
        "product": products[item_id],
        "price": prices[item_id],
        "description": fake.text(200),
        "rating": round(random.uniform(3.5, 5.0), 1),
        "reviews": random.randint(10, 500),
        "confidence": 0.45
    })


@app.get("/table-clean", response_class=HTMLResponse)
async def table_clean(request: Request):
    """Clean table structure"""
    data = [
        {"product": products[i], "price": prices[i], "stock": random.randint(0, 100)}
        for i in range(10)
    ]
    return templates.TemplateResponse("table_clean.html", {
        "request": request,
        "data": data,
        "confidence": 0.98
    })


@app.get("/table-messy", response_class=HTMLResponse)
async def table_messy(request: Request):
    """Messy table requiring LLM"""
    data = [
        {"product": products[i], "price": prices[i], "stock": random.randint(0, 100)}
        for i in range(10)
    ]
    return templates.TemplateResponse("table_messy.html", {
        "request": request,
        "data": data,
        "confidence": 0.35
    })


@app.get("/metrics")
async def metrics():
    """Return extraction confidence metrics"""
    return {
        "clean_pages": 14,
        "messy_pages": 6,
        "total_pages": 20,
        "avg_clean_confidence": 0.95,
        "avg_messy_confidence": 0.42,
        "recommendation": "Use CSS selectors for clean pages, LLM for messy pages"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
