# Test Sites Repository - Implementation Plan

## Overview

The **RipTide Test Sites** repository provides 13 self-hosted mini-sites designed to comprehensively test RipTide's web crawling and extraction capabilities. Each site targets specific features and edge cases, enabling reliable end-to-end testing without external dependencies.

**Purpose**: Create deterministic, reproducible test fixtures that validate all RipTide features—from basic crawling to complex scenarios like LLM fallback, session management, and streaming protocols.

## Site Inventory

| # | Site Name | Purpose |
|---|-----------|---------|
| 1 | **happy-path.site** | Baseline crawl + extraction with JSON-LD, pagination, sitemap |
| 2 | **selectors-vs-llm.site** | CSS selector success (70%) vs. LLM fallback (30%) |
| 3 | **static-vs-headless.site** | Intelligent routing—static extraction vs. headless browser |
| 4 | **pdfs-and-binaries.site** | PDF text extraction, table parsing, non-HTML handling |
| 5 | **redirects-canonical.site** | 301/302 chains, canonical URLs, deduplication |
| 6 | **robots-and-sitemaps.site** | robots.txt semantics, crawl-delay, sitemap discovery |
| 7 | **slowpoke-and-retries.site** | Latency, timeouts, 429 Retry-After, 5xx backoff |
| 8 | **auth-and-session.site** | Cookie/login flow, CSRF tokens, session persistence |
| 9 | **encoding-and-i18n.site** | Charsets (ISO-8859-1), RTL languages, emoji handling |
| 10 | **media-and-nonhtml.site** | Image/video/CSS resources, HTML-only extraction mode |
| 11 | **anti-bot-lite.site** | Rate limiting, header checks, politeness policies |
| 12 | **jobs-and-offers.site** | JobPosting JSON-LD, entity switching, messy HTML |
| 13 | **websocket-stream-sink** | WebSocket streaming validation (echo server) |

## Technology Stack

**Backend Frameworks**: FastAPI (Python) for rapid development and deterministic data generation

**Key Dependencies**:
- **FastAPI** - Modern async web framework
- **Faker** - Deterministic fake data (seeded)
- **Jinja2** - HTML templating
- **PyPDF2** - PDF generation for fixtures
- **Docker Compose** - Local orchestration

**Data Generation**: All sites use `FIXTURE_SEED` environment variable for reproducible content.

## Architecture

### Site Structure
Each mini-site follows a consistent pattern:

```
<site-name>/
├── app.py                 # FastAPI application
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── templates/            # Jinja2 templates
│   ├── index.html
│   ├── list.html
│   └── detail.html
└── static/              # CSS, JS, images (optional)
```

### Data Generation Pattern
```python
# Consistent seeding across all sites
from faker import Faker
import os

SEED = int(os.getenv('FIXTURE_SEED', 42))
fake = Faker()
fake.seed_instance(SEED)

# Generate deterministic events
def generate_events(count=100):
    return [create_event(i) for i in range(count)]
```

### Common Features
- **JSON-LD structured data** (Schema.org)
- **Semantic HTML** for CSS selector testing
- **Pagination** (typically 10 items per page)
- **Configurable complexity** via environment variables

## Repository Structure

```
riptide-fixtures/
├── README.md
├── docker-compose.yml              # All sites orchestrated
├── Makefile                        # Dev shortcuts
├── .env.example                    # Environment template
│
├── sites/                          # Site implementations
│   ├── happy-path.site/
│   ├── selectors-vs-llm.site/
│   ├── static-vs-headless.site/
│   ├── pdfs-and-binaries.site/
│   ├── redirects-canonical.site/
│   ├── robots-and-sitemaps.site/
│   ├── slowpoke-and-retries.site/
│   ├── auth-and-session.site/
│   ├── encoding-and-i18n.site/
│   ├── media-and-nonhtml.site/
│   ├── anti-bot-lite.site/
│   ├── jobs-and-offers.site/
│   └── websocket-stream-sink/
│
├── ground-truth/                   # Expected outputs
│   ├── happy-path.pages.jsonl
│   ├── happy-path.stats.json
│   ├── happy-path.entities.jsonl
│   └── ... (per site)
│
├── tests/                          # E2E tests
│   ├── conftest.py
│   ├── test_happy_path.py
│   ├── test_selectors_llm.py
│   └── ...
│
└── scripts/                        # Utilities
    ├── generate_ground_truth.py
    ├── health_check.sh
    └── validate_fixtures.py
```

## Quick Start

### 5-Minute Setup

```bash
# Clone the repository
git clone https://github.com/<org>/riptide-fixtures.git
cd riptide-fixtures

# Configure (optional - defaults work)
cp .env.example .env

# Start all 13 sites
docker-compose up -d --build

# Verify health (wait ~10s for startup)
make health-check

# View sites
open http://localhost:5001  # happy-path.site
open http://localhost:5002  # selectors-vs-llm.site
# ... ports 5001-5013
```

### Individual Site

```bash
# Start single site
docker-compose up -d happy-path

# View logs
docker-compose logs -f happy-path

# Stop
docker-compose down
```

## Deployment Strategy

### Option 1: Local Development (Default)
**Use case**: Developer testing, CI/CD
**Method**: Docker Compose on localhost
**Cost**: Free

```bash
# In RipTide repo
git submodule update --init fixtures
cd fixtures && docker-compose up -d
pytest tests/e2e/  # Points to http://localhost:5001-5013
```

**Pros**: Zero cost, full control, fast iteration
**Cons**: Requires local Docker

---

### Option 2: Hetzner VPS + Coolify (RECOMMENDED FOR HOSTING)
**Use case**: Permanent hosted test environment
**Cost**: **€3.49-6/month ($4-7/month)** for ALL 13 sites
**Setup time**: 45 minutes

Deploy all 13 sites on a single VPS with automatic subdomains and HTTPS:

```bash
# URLs you'll get (no domain purchase needed):
# http://happy-path.1.2.3.4.sslip.io
# http://selectors-llm.1.2.3.4.sslip.io
# ... (all 13 sites)

# One-time setup
1. Create Hetzner CAX11 VPS (€3.49/month)
2. Install Coolify (free Heroku-like UI)
3. Deploy all 13 sites via Coolify dashboard
4. Automatic HTTPS via Caddy + Let's Encrypt
```

**Pros**:
- Cheapest option by far (75% cheaper than alternatives)
- Can host 50+ sites on one VPS
- Full Docker Compose support
- Heroku-like deployment experience
- No domain purchase needed (uses sslip.io)

**Cons**:
- One-time 45 min setup
- Self-managed (but Coolify handles most tasks)

📖 **Complete setup guide**: See `DEPLOYMENT.md` in this folder

---

### Option 3: Google Cloud Run (FREE TIER)
**Use case**: Zero infrastructure management
**Cost**: **$0-8/month** (likely stays FREE)
**Setup time**: 30 minutes

Deploy 13 separate Cloud Run services with auto-generated URLs:

```bash
# URLs you'll get:
# https://happy-path-abc123.run.app
# https://selectors-llm-xyz789.run.app
# ... (all 13 sites)

# Deploy all sites
for site in sites/*/; do
  gcloud run deploy $(basename $site) \
    --source $site \
    --allow-unauthenticated
done
```

**Pros**:
- Stays in free tier (2M requests/month)
- Zero maintenance
- Scales to zero when not used
- Auto HTTPS

**Cons**:
- 1-3 second cold starts
- Requires Google Cloud account

📖 **Complete setup guide**: See `DEPLOYMENT.md` in this folder

---

### Option 4: Koyeb (FULLY MANAGED)
**Use case**: Production-ready, simple deployment
**Cost**: **$20/month** (1 free + 12 × $1.61 eco instances)
**Setup time**: 20 minutes

```bash
# URLs you'll get:
# https://happy-path.koyeb.app
# https://selectors-llm.koyeb.app
# ... (all 13 sites)

# Deploy via CLI
koyeb app init happy-path --git github.com/<org>/fixtures \
  --git-branch main --git-workdir sites/happy-path.site
```

**Pros**:
- Simplest managed option
- Global CDN (150+ locations)
- Zero cold starts
- Git-based deployment

**Cons**:
- Most expensive option

📖 **Complete setup guide**: See `DEPLOYMENT.md` in this folder

---

### Option 5: GitHub Container Registry (GHCR)
**Use case**: Fast CI builds, versioned releases
**Method**: Pre-build Docker images, publish to GHCR
**Cost**: Free

```bash
# Build and push (automated via CI)
docker build -t ghcr.io/<org>/riptide-fixture-happy:v0.1.0 sites/happy-path.site
docker push ghcr.io/<org>/riptide-fixture-happy:v0.1.0

# In docker-compose.yml
services:
  happy-path:
    image: ghcr.io/<org>/riptide-fixture-happy:v0.1.0
    # No build step needed
```

**Pros**: Fastest CI (no build time), versioned artifacts
**Cons**: Still need hosting for actual sites

---

### Recommended Approach by Budget

| Budget | Recommendation | Annual Cost |
|--------|---------------|-------------|
| **$0** | Google Cloud Run | $0 |
| **<$100/year** | Hetzner + Coolify | $48-84 |
| **<$300/year** | Koyeb | $240 |
| **Any** | Local + GHCR for CI | $0 |

### Recommended: Hybrid
- **CI/CD**: GHCR images for fast builds
- **Local dev**: docker-compose up (editable)
- **Hosted**: Hetzner or Cloud Run (your choice)

📊 **Full cost comparison & setup guides**: See `DEPLOYMENT.md` in this folder

## URL Strategy

### Port Allocation
| Site | Port | URL |
|------|------|-----|
| happy-path | 5001 | http://localhost:5001 |
| selectors-vs-llm | 5002 | http://localhost:5002 |
| static-vs-headless | 5003 | http://localhost:5003 |
| pdfs-and-binaries | 5004 | http://localhost:5004 |
| redirects-canonical | 5005 | http://localhost:5005 |
| robots-and-sitemaps | 5006 | http://localhost:5006 |
| slowpoke-and-retries | 5007 | http://localhost:5007 |
| auth-and-session | 5008 | http://localhost:5008 |
| encoding-and-i18n | 5009 | http://localhost:5009 |
| media-and-nonhtml | 5010 | http://localhost:5010 |
| anti-bot-lite | 5011 | http://localhost:5011 |
| jobs-and-offers | 5012 | http://localhost:5012 |
| websocket-stream-sink | 5013 | ws://localhost:5013 |

### Hosted URLs (No Domain Purchase Needed!)

**Hetzner VPS** (using sslip.io):
- `http://happy-path.1.2.3.4.sslip.io`
- `http://selectors-llm.1.2.3.4.sslip.io`

**Google Cloud Run**:
- `https://happy-path-abc123.run.app`
- `https://selectors-llm-xyz789.run.app`

**Koyeb**:
- `https://happy-path.koyeb.app`
- `https://selectors-llm.koyeb.app`

Configure via `BASE_URL` environment variable in tests:

```bash
# .env in RipTide tests
BASE_URL=https://happy-path.koyeb.app  # or your chosen hosting
```

## Ground Truth Management

### File Format
Each site maintains 3 golden files:

**1. Pages** (`<site>.pages.jsonl`)
```jsonl
{"url": "http://localhost:5001/", "depth": 0, "status_code": 200, "canonical_url": "http://localhost:5001/", "links_count": 15}
{"url": "http://localhost:5001/events/", "depth": 1, "status_code": 200, "canonical_url": null, "links_count": 25}
```

**2. Statistics** (`<site>.stats.json`)
```json
{
  "pages_crawled": 127,
  "pages_failed": 0,
  "domains": 1,
  "stop_reason": "max_pages",
  "extraction_method": {"static": 114, "headless": 13}
}
```

**3. Entities** (`<site>.entities.jsonl`)
```jsonl
{"type": "Event", "name": "Summer Festival 2024", "startDate": "2024-06-15", "url": "http://localhost:5001/event/1"}
{"type": "Event", "name": "Tech Conference", "startDate": "2024-07-22", "url": "http://localhost:5001/event/2"}
```

### Generation
```bash
# Regenerate ground truth after site changes
make ground-truth

# Or manually
python scripts/generate_ground_truth.py --site happy-path --output ground-truth/
```

### Validation
```bash
# Validate current output matches ground truth
pytest tests/e2e/test_happy_path.py --golden-check

# Update golden files (use with caution!)
pytest tests/e2e/test_happy_path.py --golden-update
```

## Contributing

### Adding a New Site

**1. Create site directory**
```bash
mkdir -p sites/my-new-site.site
cd sites/my-new-site.site
```

**2. Implement FastAPI app**
```python
# app.py
from fastapi import FastAPI
from faker import Faker
import os

app = FastAPI()
fake = Faker()
fake.seed_instance(int(os.getenv('FIXTURE_SEED', 42)))

@app.get("/")
async def index():
    return {"message": "My new test site"}
```

**3. Add Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**4. Update docker-compose.yml**
```yaml
services:
  my-new-site:
    build: ./sites/my-new-site.site
    ports:
      - "5014:8000"
    environment:
      - FIXTURE_SEED=${FIXTURE_SEED:-42}
```

**5. Generate ground truth**
```bash
make ground-truth SITE=my-new-site
```

**6. Create tests**
```python
# tests/test_my_new_site.py
def test_basic_crawl(riptide_client, golden_data):
    result = riptide_client.crawl("http://localhost:5014/")
    assert result.pages_crawled > 0
    assert_matches_golden(result, golden_data['my-new-site.pages.jsonl'])
```

### Guidelines
- **Deterministic data**: Always seed Faker with `FIXTURE_SEED`
- **Self-contained**: No external API dependencies
- **Documented**: Add site description to this PLAN.md
- **Tested**: Include E2E test that validates against ground truth
- **Lightweight**: Keep container size < 100MB when possible

## Integration with RipTide

### Submodule Approach
```bash
# In riptide-crawler repo
git submodule add https://github.com/<org>/riptide-fixtures fixtures
git submodule update --init --recursive

# In CI
- name: Start fixtures
  run: |
    cd fixtures
    docker-compose up -d --build
    ./scripts/health_check.sh

- name: Run E2E tests
  run: pytest tests/e2e/
  env:
    FIXTURE_BASE_URL: http://localhost
```

### Environment Variables
```bash
# .env in RipTide repo
FIXTURE_BASE_URL=http://localhost  # or https://fixtures.riptide.dev
FIXTURE_SEED=42                    # Match fixture generation seed
E2E_TIMEOUT=30                     # Test timeout (seconds)
```

## Maintenance

### Regular Tasks
- **Monthly**: Verify all sites start successfully
- **Per release**: Regenerate ground truth if extraction logic changes
- **On dependency updates**: Rebuild Docker images, test health

### Versioning
Use semantic versioning for releases:
- `v0.1.0` - Initial 6 sites (quick wins)
- `v0.2.0` - Add auth, session, LLM sites
- `v1.0.0` - Complete 13-site suite with full CI integration

Tag releases and publish to GHCR for RipTide CI consumption.

---

**Next Steps**: See [ROADMAP.md](./ROADMAP.md) for phased implementation plan.
