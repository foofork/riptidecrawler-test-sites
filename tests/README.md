# RipTide Test Sites - Testing Infrastructure

Complete testing suite for validating RipTide web crawler capabilities across 13 specialized test sites.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Utilities](#test-utilities)
- [Ground Truth Validation](#ground-truth-validation)
- [CI/CD Integration](#cicd-integration)
- [Contributing](#contributing)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Make (optional, for convenience commands)

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start all test sites
docker-compose up -d

# Wait for services to be healthy
./scripts/health_check_new.sh --wait

# Run tests
pytest tests/ -v
```

### Using Make Commands

```bash
make help              # Show all available commands
make up                # Start services and wait for health
make test              # Run all tests
make test-phase1       # Run Phase 1 tests only
make ground-truth      # Generate ground truth data
make clean             # Clean up everything
```

## Test Structure

### Test Phases

**Phase 1: Core Functionality** (Ports 5001, 5005, 5006)
- `test_happy_path.py` - Baseline crawling, JSON-LD, sitemaps
- `test_redirects.py` - Redirect chains and canonical URLs
- `test_robots.py` - robots.txt compliance and sitemap discovery

**Phase 2: Advanced Features** (Ports 5002-5004, 5007-5008)
- `test_selectors_llm.py` - CSS selectors vs LLM fallback
- `test_static_headless.py` - Static vs headless browser routing
- `test_slowpoke.py` - Slow responses, retries, backoff
- `test_auth_session.py` - Authentication and session management
- `test_pdfs.py` - PDF text extraction and binary handling

### Test Organization

```
tests/
├── conftest.py                 # Shared fixtures
├── test_happy_path.py          # 296 lines, 25 tests
├── test_redirects.py           # 299 lines, 18 tests
├── test_robots.py              # 407 lines, 22 tests
├── test_selectors_llm.py       # 245 lines, 12 tests
├── test_static_headless.py     # 215 lines, 11 tests
├── test_slowpoke.py            # 285 lines, 13 tests
├── test_auth_session.py        # 290 lines, 14 tests
├── test_pdfs.py                # 260 lines, 13 tests
├── utils/
│   ├── __init__.py
│   ├── crawl_helpers.py        # Crawling utilities
│   ├── comparison.py           # Ground truth comparison
│   ├── docker_helpers.py       # Docker health checks
│   └── jsonld_helpers.py       # JSON-LD validation
└── README.md                   # This file
```

## Running Tests

### By Phase

```bash
# Phase 1 (Core functionality)
pytest tests/ -m phase1 -v

# Phase 2 (Advanced features)
pytest tests/ -m phase2 -v
```

### By Speed

```bash
# Fast tests only (< 5 seconds each)
pytest tests/ -m "not slow" -v

# Slow tests only (integration, E2E)
pytest tests/ -m slow -v
```

### By Site

```bash
# Test specific site
pytest tests/test_happy_path.py -v
pytest tests/test_redirects.py -v

# Or using make
make test-site SITE=happy-path
```

### With Coverage

```bash
# Generate coverage report
pytest tests/ --cov=tests --cov-report=html --cov-report=term

# View report
open htmlcov/index.html

# Or using make
make test-coverage
```

### Parallel Execution

```bash
# Run tests in parallel (4 workers)
pytest tests/ -n 4 -v

# Run Phase 1 in parallel
pytest tests/ -m phase1 -n auto -v
```

## Test Utilities

### Crawl Helpers (`tests/utils/crawl_helpers.py`)

```python
from tests.utils import SimpleCrawler, extract_links, follow_redirects

# Simple breadth-first crawler
crawler = SimpleCrawler(http_client, max_pages=100)
result = crawler.crawl("http://localhost:5001/")

# Extract links from HTML
links = extract_links(soup, base_url)

# Follow redirect chain
redirect_info = follow_redirects(session, url)
```

### Comparison Engine (`tests/utils/comparison.py`)

```python
from tests.utils import ComparisonEngine, calculate_similarity

# Compare with ground truth
engine = ComparisonEngine(tolerance=0.05)
result = engine.compare_stats(actual_stats, expected_stats)
result = engine.compare_entities(actual_entities, expected_entities)

# String similarity
similarity = calculate_similarity(str1, str2)  # 0.0 to 1.0
```

### Docker Helpers (`tests/utils/docker_helpers.py`)

```python
from tests.utils import DockerHealthChecker, wait_for_services

# Check service health
checker = DockerHealthChecker()
is_healthy = checker.check_service(port=5001)

# Wait for all services
service_ports = {"happy-path": 5001, "redirects": 5005}
all_healthy = wait_for_services(service_ports, timeout=60)
```

### JSON-LD Helpers (`tests/utils/jsonld_helpers.py`)

```python
from tests.utils import extract_jsonld, validate_schema, extract_entities

# Extract all JSON-LD from page
jsonld_data = extract_jsonld(soup)

# Validate against schema
result = validate_schema(data, 'Event', ['name', 'startDate', 'location'])

# Extract entities by type
events = extract_entities(html_content, entity_type='Event')
```

## Ground Truth Validation

### Generating Ground Truth

```bash
# Generate for all Phase 1 sites
python scripts/generate_ground_truth.py --all --validate --include-sitemap

# Generate for specific site
python scripts/generate_ground_truth.py --site happy-path --validate

# Using make
make ground-truth
make ground-truth-site SITE=happy-path
```

### Ground Truth Files

```
ground-truth/
├── happy-path.pages.jsonl      # Crawled pages
├── happy-path.stats.json       # Crawl statistics
├── happy-path.entities.jsonl   # Extracted entities
├── happy-path.sitemap.json     # Sitemap coverage
├── redirects-canonical.*.json  # Similar files
└── robots-and-sitemaps.*.json  # Similar files
```

### File Formats

**Pages (JSONL)**
```jsonl
{"url": "http://localhost:5001/", "depth": 0, "status_code": 200, "links_count": 15}
{"url": "http://localhost:5001/event/1", "depth": 1, "status_code": 200, "links_count": 10}
```

**Statistics (JSON)**
```json
{
  "pages_crawled": 110,
  "pages_failed": 0,
  "domains": 1,
  "stop_reason": "max_pages",
  "extraction_methods": {"static": 110}
}
```

**Entities (JSONL)**
```jsonl
{"type": "Event", "name": "Summer Festival", "startDate": "2025-11-01", "url": "..."}
```

## CI/CD Integration

### GitHub Actions

The test suite runs automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

**Workflow Jobs:**
1. `test` - Run tests (matrix: Python 3.10, 3.11 × Phase 1, 2)
2. `ground-truth-validation` - Validate fixtures and generate ground truth
3. `coverage` - Generate coverage reports
4. `integration` - Full integration tests

### Local CI Simulation

```bash
# Run full CI pipeline locally
make ci

# Or manually
make clean
make build
make test
make validate
make ground-truth
```

## Test Development

### Adding New Tests

1. **Create test file**
   ```python
   # tests/test_my_site.py
   import pytest

   SITE_PORT = 5009

   @pytest.mark.phase2
   @pytest.mark.requires_docker
   class TestMySite:
       def test_site_is_healthy(self, health_check):
           assert health_check(SITE_PORT)
   ```

2. **Register site** in `scripts/health_check_new.sh`:
   ```bash
   declare -A SITES=(
       # ... existing sites
       ["my-site"]=5009
   )
   ```

3. **Add to ground truth** generator:
   ```python
   # scripts/generate_ground_truth.py
   SITES_CONFIG = {
       # ... existing sites
       "my-site": {
           "port": 5009,
           "expected_pages": 100,
           "expected_entities": 80,
           "entity_type": "Product"
       }
   }
   ```

4. **Run tests**
   ```bash
   pytest tests/test_my_site.py -v
   ```

### Test Markers

Use pytest markers to organize tests:

```python
@pytest.mark.phase1        # Phase 1 test
@pytest.mark.phase2        # Phase 2 test
@pytest.mark.slow          # Slow test (>10s)
@pytest.mark.requires_docker  # Needs Docker
@pytest.mark.integration   # Integration test
@pytest.mark.smoke         # Quick validation test
```

### Fixtures

Available in `conftest.py`:

- `docker_services` - Ensures Docker is running
- `http_client` - Configured HTTP session with retries
- `health_check` - Factory for checking service health
- `ground_truth_loader` - Load ground truth data
- `compare_with_ground_truth` - Compare with ground truth
- `site_url` - Generate site URLs
- `crawl_simulator` - Simple crawler for testing

## Configuration

### Environment Variables

```bash
# Base URL for all sites
export BASE_URL=http://localhost

# Fixture seed for deterministic data
export FIXTURE_SEED=42

# Test timeout (seconds)
export E2E_TIMEOUT=30
```

### pytest.ini

```ini
[pytest]
markers =
    phase1: Phase 1 sites
    phase2: Phase 2 sites
    slow: Slow tests
    requires_docker: Needs Docker

addopts =
    -ra
    --strict-markers
    --tb=short
    --maxfail=10

timeout = 300
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
docker-compose logs --tail=50

# Restart services
make restart

# Check specific service
docker-compose logs -f happy-path
```

### Tests Failing

```bash
# Run with verbose output
pytest tests/ -vv --tb=long

# Run single test
pytest tests/test_happy_path.py::TestHappyPath::test_site_is_healthy -vv

# Check health status
./scripts/health_check_new.sh
```

### Performance Issues

```bash
# Run tests in parallel
pytest tests/ -n auto

# Skip slow tests
pytest tests/ -m "not slow"

# Increase timeouts
export E2E_TIMEOUT=60
```

## Best Practices

1. **Always start Docker** before running tests
   ```bash
   make up  # Starts and waits for health
   ```

2. **Use markers** to organize tests
   ```python
   @pytest.mark.phase1
   @pytest.mark.slow
   ```

3. **Validate ground truth** after site changes
   ```bash
   make validate
   make ground-truth
   ```

4. **Run fast tests first** during development
   ```bash
   pytest tests/ -m "not slow" --maxfail=1
   ```

5. **Clean up** between test runs if issues occur
   ```bash
   make clean
   make up
   ```

## Contributing

### Running Full Test Suite

```bash
# Clean environment
make clean

# Build and start services
make build
make up

# Run all tests
make test

# Generate ground truth
make ground-truth

# Validate everything
make validate
```

### Before Submitting PR

1. All tests pass: `make test`
2. Ground truth valid: `make validate`
3. Coverage >90%: `make test-coverage`
4. Code formatted: `black tests/`
5. No linting errors: `flake8 tests/`

## Additional Resources

- [Plan.md](../Plan.md) - Complete implementation plan
- [Roadmap.md](../Roadmap.md) - Development roadmap
- [Deployment.md](../Deployment.md) - Hosting options
- [Docker Compose](../docker-compose.yml) - Service configuration

## Support

For issues or questions:
1. Check this README
2. Review existing tests for examples
3. Check GitHub Issues
4. Ask in project discussions

---

**Test Suite Status**: 128+ tests across 8 test files covering 8 test sites

**Coverage Target**: >90% for all core functionality

**Maintained By**: RipTide Testing Team
