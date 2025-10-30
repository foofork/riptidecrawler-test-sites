# RipTide Test Sites - Testing Guide

Comprehensive guide to testing strategy, validation, and quality assurance.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Types](#test-types)
3. [Ground Truth Validation](#ground-truth-validation)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

---

## Testing Philosophy

### Core Principles

1. **Deterministic Data**: All tests use seeded data (seed=42)
2. **Ground Truth Validation**: Compare against known-good outputs
3. **Isolated Tests**: Each test is independent
4. **Fast Feedback**: Tests complete in <30 seconds
5. **Reproducible**: Same results every time

### Test Pyramid

```
           ╱────────╲
          ╱ E2E Tests ╲       (13 sites × 3 tests = ~40 tests)
         ╱────────────╲
        ╱ Integration  ╲      (API endpoint tests)
       ╱────────────────╲
      ╱   Unit Tests     ╲    (Data generation, models)
     ╱────────────────────╲
```

---

## Test Types

### 1. Health Check Tests

Verify basic site availability and health.

```python
# tests/test_health.py
import pytest
import requests

SITES = [
    ("ecommerce", 5001),
    ("blog", 5002),
    ("social", 5003),
    # ... all 13 sites
]

@pytest.mark.parametrize("site_name,port", SITES)
def test_site_health(site_name, port):
    """Test site health endpoint"""
    url = f"http://localhost:{port}/api/health"
    response = requests.get(url, timeout=5)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["site"] == site_name
    assert data["data_generated"] is True
```

### 2. Ground Truth Tests

Validate data against golden files.

```python
# tests/test_ground_truth.py
import pytest
import requests
import json
from pathlib import Path

@pytest.fixture
def ground_truth_data():
    """Load ground truth files"""
    data = {}
    for site_dir in Path("sites").iterdir():
        if site_dir.is_dir():
            gt_file = site_dir / "ground-truth" / "data.json"
            if gt_file.exists():
                with open(gt_file) as f:
                    data[site_dir.name] = json.load(f)
    return data

@pytest.mark.parametrize("site_name,port", SITES)
def test_ground_truth_match(site_name, port, ground_truth_data):
    """Test site data matches ground truth"""
    url = f"http://localhost:{port}/api/ground-truth"
    response = requests.get(url)

    assert response.status_code == 200
    actual = response.json()
    expected = ground_truth_data[site_name]

    # Compare seed
    assert actual["seed"] == 42
    assert expected["seed"] == 42

    # Compare data (flexible comparison)
    assert len(actual["items"]) == len(expected["items"])
    assert actual["items"] == expected["items"]
```

### 3. API Endpoint Tests

Validate all API endpoints work correctly.

```python
# tests/test_api_endpoints.py
import pytest
import requests

def test_ecommerce_products():
    """Test products API"""
    response = requests.get("http://localhost:5001/api/products")
    assert response.status_code == 200

    data = response.json()
    assert "products" in data
    assert len(data["products"]) > 0

    # Validate product structure
    product = data["products"][0]
    assert "id" in product
    assert "name" in product
    assert "price" in product

def test_blog_posts():
    """Test blog posts API"""
    response = requests.get("http://localhost:5002/api/posts")
    assert response.status_code == 200

    data = response.json()
    assert "posts" in data
    assert len(data["posts"]) == 200  # Expected count

def test_pagination():
    """Test pagination works"""
    # Page 1
    response = requests.get("http://localhost:5001/api/products?page=1&per_page=10")
    page1 = response.json()["products"]

    # Page 2
    response = requests.get("http://localhost:5001/api/products?page=2&per_page=10")
    page2 = response.json()["products"]

    # Should be different items
    assert page1[0]["id"] != page2[0]["id"]
```

### 4. UI Rendering Tests

Verify HTML pages render correctly.

```python
# tests/test_ui_rendering.py
import pytest
import requests
from bs4 import BeautifulSoup

def test_homepage_renders():
    """Test homepage HTML"""
    response = requests.get("http://localhost:5001/")
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")

    # Check page title
    assert soup.title.string == "E-commerce Site"

    # Check navigation exists
    nav = soup.find("nav")
    assert nav is not None

    # Check products displayed
    products = soup.find_all(class_="product")
    assert len(products) > 0

def test_detail_page():
    """Test detail page renders"""
    response = requests.get("http://localhost:5001/products/1")
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")

    # Check product details
    assert soup.find(class_="product-name") is not None
    assert soup.find(class_="product-price") is not None
```

### 5. JSON-LD Validation Tests

Ensure structured data is correct.

```python
# tests/test_structured_data.py
import pytest
import requests
import json
from bs4 import BeautifulSoup

def test_product_jsonld():
    """Test Product JSON-LD"""
    response = requests.get("http://localhost:5001/products/1")
    soup = BeautifulSoup(response.text, "html.parser")

    # Find JSON-LD script
    jsonld_script = soup.find("script", {"type": "application/ld+json"})
    assert jsonld_script is not None

    # Parse JSON-LD
    data = json.loads(jsonld_script.string)

    # Validate schema
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "Product"
    assert "name" in data
    assert "price" in data
    assert "priceCurrency" in data

def test_blog_article_jsonld():
    """Test BlogPosting JSON-LD"""
    response = requests.get("http://localhost:5002/posts/1")
    soup = BeautifulSoup(response.text, "html.parser")

    jsonld = soup.find("script", {"type": "application/ld+json"})
    data = json.loads(jsonld.string)

    assert data["@type"] == "BlogPosting"
    assert "headline" in data
    assert "author" in data
    assert "datePublished" in data
```

### 6. Performance Tests

Ensure sites respond quickly.

```python
# tests/test_performance.py
import pytest
import requests
import time

def test_response_time():
    """Test sites respond within 500ms"""
    for port in range(5001, 5014):
        start = time.time()
        response = requests.get(f"http://localhost:{port}/")
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 500, f"Port {port} took {elapsed}ms"

def test_concurrent_requests():
    """Test sites handle concurrent requests"""
    import concurrent.futures

    def fetch(url):
        return requests.get(url)

    urls = [f"http://localhost:5001/products/{i}" for i in range(1, 21)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        responses = list(executor.map(fetch, urls))

    # All should succeed
    assert all(r.status_code == 200 for r in responses)
```

---

## Ground Truth Validation

### What is Ground Truth?

Ground truth files are **golden datasets** that represent expected outputs. They enable:

1. **Regression testing**: Detect unintended changes
2. **Deterministic validation**: Same results every time
3. **CI/CD confidence**: Automated validation

### File Format

```json
{
  "site": "ecommerce",
  "seed": 42,
  "version": "1.0.0",
  "generated_at": "2024-01-15T10:30:00Z",
  "items": [
    {
      "id": 1,
      "name": "Product Name",
      "price": 29.99,
      "description": "Product description"
    }
  ],
  "metadata": {
    "total_items": 100,
    "categories": 10,
    "users": 50
  }
}
```

### Generating Ground Truth

```bash
# Regenerate all ground truth files
make ground-truth

# Or manually per site
curl http://localhost:5001/api/ground-truth > sites/ecommerce/ground-truth/data.json
```

### Validation Script

```python
# scripts/validate_fixtures.py
import json
import requests
from pathlib import Path

def validate_site(site_name, port):
    """Validate site against ground truth"""
    # Fetch current data
    response = requests.get(f"http://localhost:{port}/api/ground-truth")
    current = response.json()

    # Load ground truth
    gt_file = Path(f"sites/{site_name}/ground-truth/data.json")
    with open(gt_file) as f:
        expected = json.load(f)

    # Compare
    errors = []

    if current["seed"] != expected["seed"]:
        errors.append(f"Seed mismatch: {current['seed']} != {expected['seed']}")

    if len(current["items"]) != len(expected["items"]):
        errors.append(f"Item count mismatch: {len(current['items'])} != {len(expected['items'])}")

    if current["items"] != expected["items"]:
        errors.append("Item data mismatch")

    return errors

# Run validation
for site_name, port in SITES:
    errors = validate_site(site_name, port)
    if errors:
        print(f"❌ {site_name}: {', '.join(errors)}")
    else:
        print(f"✅ {site_name}: OK")
```

---

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_ecommerce.py -v

# Run specific test
pytest tests/test_ecommerce.py::test_health -v
```

### Test Modes

```bash
# Fast mode (skip slow tests)
pytest tests/ -m "not slow"

# Integration tests only
pytest tests/ -m integration

# Unit tests only
pytest tests/ -m unit

# Smoke tests (quick validation)
pytest tests/ -m smoke
```

### Coverage

```bash
# Run with coverage
pytest tests/ --cov=sites --cov-report=html

# View coverage report
open htmlcov/index.html

# Coverage report in terminal
pytest tests/ --cov=sites --cov-report=term
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest tests/ -n auto

# Use 4 workers
pytest tests/ -n 4
```

---

## Writing Tests

### Test Structure

```python
# tests/test_example.py
import pytest
import requests

# Fixtures
@pytest.fixture
def api_url():
    return "http://localhost:5001"

@pytest.fixture
def sample_data():
    return {"name": "Test", "value": 123}

# Tests
def test_example(api_url, sample_data):
    """Test description"""
    # Arrange
    url = f"{api_url}/api/endpoint"

    # Act
    response = requests.post(url, json=sample_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["success"] is True

# Parameterized tests
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

### Best Practices

1. **Use descriptive names**: `test_user_login_with_valid_credentials()`
2. **One assertion per concept**: Focus each test
3. **Arrange-Act-Assert**: Clear test structure
4. **Use fixtures**: Share setup code
5. **Parameterize**: Test multiple inputs
6. **Mark tests**: Use `@pytest.mark` for categories

### Test Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_expensive_operation():
    pass

# Mark integration tests
@pytest.mark.integration
def test_full_workflow():
    pass

# Mark smoke tests
@pytest.mark.smoke
def test_critical_path():
    pass

# Skip tests conditionally
@pytest.mark.skipif(condition, reason="...")
def test_optional():
    pass
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt

      - name: Start test sites
        run: |
          docker-compose up -d --build
          sleep 10  # Wait for startup

      - name: Health check
        run: make health-check

      - name: Run tests
        run: pytest tests/ -v --cov=sites --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Stop sites
        if: always()
        run: docker-compose down
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - validate

test:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker-compose up -d --build
    - sleep 10
    - docker exec test-site-ecommerce curl http://localhost:8000/api/health
    - pytest tests/ -v
  after_script:
    - docker-compose down

validate:
  stage: validate
  script:
    - python scripts/validate_fixtures.py
```

---

## Troubleshooting

### Tests Fail with Connection Errors

```bash
# Verify sites are running
make ps

# Check health
make health-check

# View logs
make logs

# Restart sites
make restart
```

### Ground Truth Mismatch

```bash
# Regenerate ground truth
make ground-truth

# Compare differences
git diff sites/ecommerce/ground-truth/data.json

# Commit if intentional
git add sites/ecommerce/ground-truth/data.json
git commit -m "test: update ground truth for ecommerce"
```

### Flaky Tests

```bash
# Run test multiple times
pytest tests/test_flaky.py --count=10

# Add retries
pytest tests/ --reruns 3

# Increase timeouts
requests.get(url, timeout=10)  # was 5
```

### Port Conflicts

```bash
# Check ports
lsof -i :5001-5013

# Change ports in .env
ECOMMERCE_PORT=6001
docker-compose up -d

# Update tests
BASE_PORT=6000  # in conftest.py
```

---

## Test Metrics

### Coverage Goals

- **Overall coverage**: >80%
- **Critical paths**: 100%
- **API endpoints**: >90%
- **Data generation**: >85%

### Performance Benchmarks

- **Health check**: <100ms
- **Homepage load**: <500ms
- **API response**: <200ms
- **Full test suite**: <60s

---

## Resources

- **pytest Docs**: https://docs.pytest.org/
- **requests Docs**: https://requests.readthedocs.io/
- **Beautiful Soup**: https://www.crummy.com/software/BeautifulSoup/
- **Coverage.py**: https://coverage.readthedocs.io/

---

## Getting Help

- **Test failures**: Open issue with logs
- **New test patterns**: Check existing tests first
- **CI/CD issues**: Review workflow logs
- **Questions**: GitHub Discussions
