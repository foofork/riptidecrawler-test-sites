# RipTide Test Sites - Development Guide

Guide for contributors and developers extending the test site platform.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Creating a New Site](#creating-a-new-site)
4. [Modifying Existing Sites](#modifying-existing-sites)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Troubleshooting](#troubleshooting)

---

## Development Setup

### Prerequisites

- Python 3.11+
- Docker Desktop 4.0+ or Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Make (optional but recommended)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/riptide-test-sites.git
cd riptide-test-sites

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -r tests/requirements.txt

# Copy environment template
cp .env.example .env

# Start all sites
make up

# Verify everything works
make health-check
make test
```

### Development Workflow

```bash
# Start sites in development mode (with auto-reload)
make dev

# Make changes to a site
vim sites/ecommerce/app/main.py

# Rebuild specific site
docker-compose build ecommerce
docker-compose restart ecommerce

# View logs
make logs-ecommerce

# Test your changes
pytest tests/test_ecommerce.py -v

# Regenerate ground truth if data changed
make ground-truth
```

---

## Architecture Overview

### Site Structure

Each site follows this pattern:

```
sites/<site-name>/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── data_generator.py   # Faker-based data generation
│   └── routes.py            # API endpoints
├── templates/
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Homepage
│   ├── list.html            # List/collection page
│   └── detail.html          # Detail page
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── ground-truth/
│   └── data.json            # Expected test data
├── Dockerfile
├── requirements.txt
├── .env                     # Site-specific config
└── README.md
```

### Data Flow

```
┌─────────────────┐
│ FastAPI Request │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Route Handler   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Generator  │◄────── Faker (seed=42)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Jinja2 Template │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTML Response  │
└─────────────────┘
```

### Key Principles

1. **Deterministic Data**: Always seed Faker with 42
2. **Self-Contained**: No external API calls or databases
3. **Consistent Structure**: All sites follow same pattern
4. **Health Endpoints**: Every site implements `/api/health`
5. **Ground Truth**: Export data via `/api/ground-truth`

---

## Creating a New Site

### Step 1: Copy Template

```bash
# Use template as starting point
cp -r sites/template sites/my-new-site

# Or copy similar existing site
cp -r sites/ecommerce sites/my-new-site
```

### Step 2: Implement FastAPI App

```python
# sites/my-new-site/app/main.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from faker import Faker
import os

app = FastAPI(title="My New Site")

# Deterministic data generation
SEED = int(os.getenv('FIXTURE_SEED', 42))
fake = Faker()
Faker.seed(SEED)

# Templates
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Generate data
def generate_items(count=100):
    """Generate deterministic items"""
    items = []
    for i in range(count):
        items.append({
            "id": i + 1,
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "created_at": fake.date_time_this_year().isoformat(),
        })
    return items

# Store in memory
ITEMS = generate_items()

@app.get("/")
async def index(request: Request):
    """Homepage"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "items": ITEMS[:10],  # Show first 10
        "total": len(ITEMS)
    })

@app.get("/items")
async def list_items(request: Request, page: int = 1, per_page: int = 10):
    """Paginated items list"""
    start = (page - 1) * per_page
    end = start + per_page
    items = ITEMS[start:end]

    return templates.TemplateResponse("list.html", {
        "request": request,
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": len(ITEMS),
        "has_next": end < len(ITEMS)
    })

@app.get("/items/{item_id}")
async def item_detail(request: Request, item_id: int):
    """Item detail page"""
    item = next((i for i in ITEMS if i["id"] == item_id), None)
    if not item:
        return {"error": "Item not found"}, 404

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "item": item
    })

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "site": "my-new-site",
        "data_generated": len(ITEMS) > 0,
        "total_items": len(ITEMS)
    }

@app.get("/api/ground-truth")
async def ground_truth():
    """Export ground truth data"""
    return {
        "site": "my-new-site",
        "seed": SEED,
        "items": ITEMS
    }

@app.get("/api/stats")
async def stats():
    """Site statistics"""
    return {
        "total_items": len(ITEMS),
        "seed": SEED,
        "site": "my-new-site"
    }
```

### Step 3: Create Templates

```html
<!-- sites/my-new-site/templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My New Site{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/items">Items</a>
    </nav>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>Test Site - Generated with Faker (seed=42)</p>
    </footer>
</body>
</html>
```

```html
<!-- sites/my-new-site/templates/index.html -->
{% extends "base.html" %}

{% block title %}Home - My New Site{% endblock %}

{% block content %}
<h1>Welcome to My New Site</h1>
<p>Total items: {{ total }}</p>

<h2>Recent Items</h2>
<ul>
{% for item in items %}
    <li>
        <a href="/items/{{ item.id }}">{{ item.name }}</a>
        <p>{{ item.description }}</p>
    </li>
{% endfor %}
</ul>

<a href="/items">View All Items</a>
{% endblock %}
```

### Step 4: Add Dockerfile

```dockerfile
# sites/my-new-site/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 5: Add to docker-compose.yml

```yaml
# Add to docker-compose.yml
services:
  # ... existing services ...

  my-new-site:
    build: ./sites/my-new-site
    container_name: test-site-my-new-site
    ports:
      - "5014:8000"
    environment:
      - SITE_NAME=my-new-site
      - FAKER_SEED=42
      - PORT=8000
      - DATA_SIZE=${MY_NEW_SITE_DATA_SIZE:-100}
      - DEBUG=true
    volumes:
      - ./sites/my-new-site:/app
    networks:
      - test-sites-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 6: Generate Ground Truth

```bash
# Start site
docker-compose up -d my-new-site

# Generate ground truth
curl http://localhost:5014/api/ground-truth > sites/my-new-site/ground-truth/data.json

# Or use script
make ground-truth SITE=my-new-site
```

### Step 7: Create Tests

```python
# tests/test_my_new_site.py
import pytest
import requests
import json

BASE_URL = "http://localhost:5014"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["site"] == "my-new-site"
    assert data["data_generated"] is True

def test_homepage():
    """Test homepage renders"""
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert "My New Site" in response.text

def test_items_list():
    """Test items list endpoint"""
    response = requests.get(f"{BASE_URL}/items")
    assert response.status_code == 200
    assert "Items" in response.text

def test_ground_truth():
    """Test ground truth matches expected"""
    response = requests.get(f"{BASE_URL}/api/ground-truth")
    assert response.status_code == 200

    data = response.json()
    assert data["seed"] == 42
    assert len(data["items"]) == 100

    # Compare with golden file
    with open("sites/my-new-site/ground-truth/data.json") as f:
        expected = json.load(f)

    assert data == expected

def test_pagination():
    """Test pagination works"""
    response = requests.get(f"{BASE_URL}/items?page=1&per_page=10")
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/items?page=2&per_page=10")
    assert response.status_code == 200
```

### Step 8: Update Documentation

```bash
# Add to README.md site table
| 14 | **My New Site** | 5014 | Custom feature testing | 100 items |

# Add to Plan.md
- Site 14: **my-new-site** - Custom feature testing

# Update Makefile
SITES := ecommerce blog social ... my-new-site
```

---

## Modifying Existing Sites

### Change Data Size

```bash
# Option 1: Environment variable
docker-compose up -d -e ECOMMERCE_DATA_SIZE=200

# Option 2: .env file
echo "ECOMMERCE_DATA_SIZE=200" >> .env
docker-compose restart ecommerce

# Option 3: docker-compose.yml
services:
  ecommerce:
    environment:
      - DATA_SIZE=200
```

### Add New Endpoint

```python
# sites/ecommerce/app/main.py

@app.get("/api/search")
async def search(q: str):
    """Search products by name"""
    results = [
        p for p in PRODUCTS
        if q.lower() in p["name"].lower()
    ]
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }
```

### Add JSON-LD Structured Data

```html
<!-- templates/detail.html -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{ product.name }}",
  "description": "{{ product.description }}",
  "price": "{{ product.price }}",
  "priceCurrency": "USD"
}
</script>
```

### Update Ground Truth

```bash
# After changing data generation
docker-compose restart ecommerce
make ground-truth SITE=ecommerce

# Or manually
curl http://localhost:5001/api/ground-truth > sites/ecommerce/ground-truth/data.json
```

---

## Testing

### Run All Tests

```bash
make test
```

### Run Specific Test

```bash
pytest tests/test_ecommerce.py -v
pytest tests/test_ecommerce.py::test_health -v
```

### Test with Coverage

```bash
pytest tests/ --cov=sites --cov-report=html
open htmlcov/index.html
```

### Ground Truth Validation

```bash
# Validate all sites
make validate

# Validate specific site
python scripts/validate_fixtures.py --site ecommerce
```

---

## Code Style

### Python

We follow PEP 8 with these tools:

```bash
# Install tools
pip install black flake8 isort mypy

# Format code
black sites/

# Sort imports
isort sites/

# Lint
flake8 sites/

# Type check
mypy sites/
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_CASE`
- **Variables**: `snake_case`

### Documentation

```python
def generate_products(count: int = 100) -> list[dict]:
    """
    Generate deterministic product data.

    Args:
        count: Number of products to generate

    Returns:
        List of product dictionaries

    Example:
        >>> products = generate_products(10)
        >>> len(products)
        10
    """
    pass
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :5001

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "6001:8000"
```

### Container Won't Start

```bash
# View detailed logs
docker-compose logs ecommerce

# Check Dockerfile
docker build -t test-build sites/ecommerce/

# Rebuild without cache
docker-compose build --no-cache ecommerce
docker-compose up -d ecommerce
```

### Data Not Deterministic

```bash
# Verify seed is set
docker-compose exec ecommerce env | grep SEED

# Ensure Faker.seed() is called
# sites/ecommerce/app/data_generator.py
from faker import Faker
fake = Faker()
Faker.seed(42)  # ← Must be called!
```

### Ground Truth Mismatch

```bash
# Regenerate ground truth
make ground-truth

# Or manually
docker-compose restart ecommerce
sleep 2
curl http://localhost:5001/api/ground-truth > sites/ecommerce/ground-truth/data.json

# Verify
git diff sites/ecommerce/ground-truth/data.json
```

---

## Git Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/new-site-my-feature

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "feat(my-new-site): add search functionality"

# Push
git push origin feature/new-site-my-feature

# Create PR
# ... open PR in GitHub ...
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(ecommerce): add search endpoint
fix(blog): correct pagination bug
docs: update deployment guide
test(social): add integration tests
chore: update dependencies
```

---

## Contributing Checklist

Before submitting a PR:

- [ ] Code follows style guide
- [ ] All tests pass (`make test`)
- [ ] Ground truth generated (`make ground-truth`)
- [ ] Documentation updated
- [ ] Health check works (`make health-check`)
- [ ] Site added to README.md
- [ ] Dockerfile optimized
- [ ] Environment variables documented

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Faker Docs**: https://faker.readthedocs.io/
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **Docker Docs**: https://docs.docker.com/
- **pytest Docs**: https://docs.pytest.org/

---

## Getting Help

- **Issues**: https://github.com/your-org/riptide-test-sites/issues
- **Discussions**: https://github.com/your-org/riptide-test-sites/discussions
- **Email**: your-team@example.com
