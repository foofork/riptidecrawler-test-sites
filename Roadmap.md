# Test Sites Repository - Implementation Roadmap

## Overview

**Goal**: Build 13 self-hosted test sites in 3 weeks, deployed to GHCR, integrated with RipTide CI.

**Approach**: Phased rollout starting with quick wins, then core features, finally specialized sites.

**Success Criteria**:
- All sites containerized and health-checked
- Ground truth generated and validated
- E2E tests passing in RipTide CI
- <5 minute local setup time

---

## Phase 1 (Week 1): Quick Wins - Foundation

**Timeline**: Days 1-7 (Apr 1-7, 2024)
**Goal**: Get 3 sites working end-to-end with full CI integration

### Sites to Build

#### 1.1 happy-path.site (Days 1-2)
**Why first**: Simplest baseline, establishes patterns for other sites

**Features**:
- Index page with event listings
- Pagination (10 events per page, 10 pages = 100 total)
- Detail pages with JSON-LD Event schema
- `sitemap.xml` with all URLs
- `robots.txt` (allow all)
- Canonical URLs on detail pages

**Implementation**:
```python
# FastAPI app with Faker-seeded events
@app.get("/")  # Index
@app.get("/events/")  # Paginated list
@app.get("/events/{id}")  # Event detail with JSON-LD
@app.get("/sitemap.xml")
@app.get("/robots.txt")
```

**Time**: 8 hours (app + templates + Dockerfile + golden files)

**Golden files**:
- `happy-path.pages.jsonl` (110 lines: 1 index + 10 list + 100 detail - 1 canonical)
- `happy-path.stats.json` (pages_crawled: 110, domains: 1)
- `happy-path.entities.jsonl` (100 events)

**Success criteria**:
- ✅ Spider crawls 110 pages
- ✅ All 100 events extracted with JSON-LD
- ✅ Sitemap discovered and parsed
- ✅ Canonical URLs deduplicated

---

#### 1.2 redirects-canonical.site (Days 3-4)
**Why second**: Tests deduplication logic, common in real sites

**Features**:
- 301 permanent redirects (`/old-event/1` → `/events/1`)
- 302 temporary redirects (`/temp/2` → `/events/2`)
- Redirect chains (3-hop max: `/a` → `/b` → `/c` → `/events/3`)
- Canonical link tags (same page, different URLs)
- Hash-only variants (`/events/1#comments` → `/events/1`)
- Cross-pagination canonical (`/events/?page=2&sort=date` → `/events/?page=2`)

**Implementation**:
```python
@app.get("/old-event/{id}")  # 301 to /events/{id}
@app.get("/temp/{id}")       # 302 to /events/{id}
@app.get("/chain/{step}/{id}")  # Multi-hop redirects
```

**Time**: 6 hours

**Golden files**:
- `redirects-canonical.pages.jsonl` (50 unique pages, 150 URLs crawled)
- `redirects-canonical.stats.json` (pages_crawled: 50, redirects_followed: 100)

**Success criteria**:
- ✅ Redirect chains resolved correctly
- ✅ `final_url` != `requested_url` where applicable
- ✅ Canonical URLs reduce 150 fetches to 50 unique pages
- ✅ No duplicate entities extracted

---

#### 1.3 robots-and-sitemaps.site (Days 5-7)
**Why third**: Critical for polite crawling, tests policy adherence

**Features**:
- `robots.txt` with:
  - Disallow: `/admin/`, `/private/`
  - Allow: `/admin/public/` (override)
  - Crawl-delay: 2 (seconds)
- Sitemap index (`/sitemap-index.xml`) referencing:
  - `/sitemap-pages.xml` (50 pages)
  - `/sitemap-events.xml` (100 events)
- Mix of allowed/disallowed pages in HTML links

**Implementation**:
```python
@app.get("/robots.txt")
@app.get("/sitemap-index.xml")
@app.get("/sitemap-pages.xml")
@app.get("/sitemap-events.xml")
@app.get("/admin/secret")  # Should never be crawled
@app.get("/admin/public/info")  # Should be crawled
```

**Time**: 8 hours (robots parsing, crawl-delay timing)

**Golden files**:
- `robots-sitemaps.pages.jsonl` (151 pages: 50 static + 100 events + 1 public admin)
- `robots-sitemaps.stats.json` (pages_crawled: 151, disallowed_skipped: 25)

**Success criteria**:
- ✅ Disallowed URLs never fetched (check logs)
- ✅ Allow override works (`/admin/public/` crawled)
- ✅ Crawl-delay roughly respected (~2s between requests to same domain)
- ✅ Sitemap URLs discovered and matched

---

### Deliverables (End of Week 1)

**Code**:
- 3 FastAPI sites containerized
- `docker-compose.yml` with 3 services
- Makefile targets: `make up`, `make health-check`, `make ground-truth`

**Tests**:
- `tests/test_happy_path.py` (5 assertions)
- `tests/test_redirects.py` (4 assertions)
- `tests/test_robots.py` (4 assertions)

**Documentation**:
- Updated PLAN.md with site details
- README.md with quick start
- Ground truth files committed

**CI Integration**:
- GitHub Actions workflow to:
  1. Start fixtures via docker-compose
  2. Run health checks
  3. Execute pytest
  4. Publish coverage

**Time estimate**: 22 hours total (dev) + 6 hours (testing/docs) = **28 hours**

---

## Phase 2 (Week 2): Core Features - Complexity

**Timeline**: Days 8-14 (Apr 8-14, 2024)
**Goal**: Add 5 sites covering retries, extraction strategies, sessions, content types

### Sites to Build

#### 2.1 slowpoke-and-retries.site (Days 8-9)
**Features**:
- `/delay/<ms>` - Artificial delay endpoint (100ms, 500ms, 2000ms)
- `/chunked` - Chunked transfer encoding response
- `/status/429` - Rate limit with `Retry-After: 2` header
- `/status/503` - Server error (should trigger retry with backoff)
- `/timeout` - Hangs for 60s (exceeds typical timeout)

**Implementation**:
```python
import asyncio
from fastapi.responses import StreamingResponse

@app.get("/delay/{ms}")
async def delay(ms: int):
    await asyncio.sleep(ms / 1000)
    return {"delayed_ms": ms}

@app.get("/status/429")
async def rate_limit(response: Response):
    response.status_code = 429
    response.headers["Retry-After"] = "2"
    return {"error": "Rate limited"}
```

**Time**: 6 hours

**Success criteria**:
- ✅ Delays respected (verify `fetch_time_ms` in results)
- ✅ 429 triggers retry after 2s (check logs)
- ✅ 503 retries with exponential backoff
- ✅ Timeout URLs marked as failed in stats

---

#### 2.2 selectors-vs-llm.site (Days 9-10)
**Features**:
- 10 event detail pages
- 7 pages use consistent CSS classes (`.event-title`, `.event-date`)
- 3 pages use unpredictable HTML (needs LLM extraction)
- Track extraction method (selector vs. LLM) in metadata

**Implementation**:
```python
# Template A (7 events) - clean structure
<div class="event-title">Summer Fest</div>
<time class="event-date">2024-06-15</time>

# Template B (3 events) - messy structure
<section><h2>Event: <em>Winter Gala</em></h2>
Happening on <strong>2024-12-20</strong> at the venue</section>
```

**Time**: 8 hours (requires LLM integration testing)

**Success criteria**:
- ✅ 7 events extracted via CSS selectors (confidence: 1.0)
- ✅ 3 events extracted via LLM (confidence: 0.8-0.95)
- ✅ `extraction_method` field populated
- ✅ All 10 events have complete data

---

#### 2.3 static-vs-headless.site (Days 11-12)
**Features**:
- 20 event listings (static HTML)
- 5 event details render critical text via JavaScript
- Lightweight anti-bot check (`navigator.webdriver` detection)
- Require headless for JS pages, allow static for others

**Implementation**:
```python
# Static list pages
@app.get("/events/")

# Detail pages with JS requirement flag
@app.get("/events/{id}")
# Template conditionally renders:
# - Static: Full content in HTML
# - JS-required: Content loaded via fetch() after DOMContentLoaded
```

**JavaScript snippet**:
```javascript
if (window.needsJS) {
  fetch('/api/event-content/' + eventId)
    .then(r => r.json())
    .then(data => {
      document.querySelector('.event-description').textContent = data.description;
    });
}
```

**Time**: 10 hours (headless routing logic)

**Success criteria**:
- ✅ 15 pages extracted via static engine
- ✅ 5 pages extracted via headless (marked in stats)
- ✅ Anti-bot check doesn't block headless (allowlisted UA)
- ✅ `extraction_method.static: 15, headless: 5` in stats

---

#### 2.4 auth-and-session.site (Days 12-13)
**Features**:
- Public landing page
- `/login` (GET) - Renders login form with CSRF token
- `/session` (POST) - Sets session cookie on valid login
- `/events/protected/{id}` - Requires session cookie
- Session persists across requests (Redis-backed or in-memory)

**Implementation**:
```python
from fastapi import Cookie, Form
import secrets

sessions = {}  # In-memory for simplicity

@app.get("/login")
async def login_form():
    csrf_token = secrets.token_hex(16)
    sessions[csrf_token] = {"csrf": True}
    return {"csrf_token": csrf_token}

@app.post("/session")
async def create_session(csrf: str = Form(), response: Response):
    if csrf in sessions:
        session_id = secrets.token_hex(16)
        sessions[session_id] = {"authenticated": True}
        response.set_cookie("session", session_id)
        return {"status": "logged in"}
    return {"error": "invalid CSRF"}, 403

@app.get("/events/protected/{id}")
async def protected_event(id: int, session: str = Cookie(None)):
    if session in sessions and sessions[session].get("authenticated"):
        return {"event_id": id, "title": f"Protected Event {id}"}
    return {"error": "unauthorized"}, 401
```

**Time**: 8 hours

**Success criteria**:
- ✅ CSRF token extracted from login form
- ✅ Session cookie set after POST
- ✅ Protected pages accessible with session
- ✅ Session persists across crawl (not lost between requests)

---

#### 2.5 pdfs-and-binaries.site (Days 13-14)
**Features**:
- Index page with links to PDFs, images, videos
- 3 PDFs with:
  - Plain text paragraphs
  - Tables (2-3 columns)
  - Mixed content
- 5 images (PNG, JPG)
- 2 video links (MP4 - not fetched, just linked)
- Test `Content-Type` detection and skip logic

**Implementation**:
```python
from reportlab.pdfgen import canvas
from io import BytesIO

@app.get("/report.pdf")
async def pdf_report():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Annual Report 2024")
    p.drawString(100, 700, "Revenue: $1.2M")
    # Add table data
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf")

@app.get("/image.png")
async def image():
    # Return 1x1 transparent PNG
    return FileResponse("static/pixel.png")
```

**Time**: 6 hours

**Success criteria**:
- ✅ PDF text extracted (verify "Annual Report" in content)
- ✅ Tables parsed (at least rows/columns detected)
- ✅ Images skipped (or metadata recorded if `full_resources: true`)
- ✅ Videos not fetched (link recorded only)

---

### Deliverables (End of Week 2)

**Code**: 5 additional sites (8 total)

**Tests**: 5 new test files with LLM, headless, session assertions

**Docker**: Updated `docker-compose.yml` with ports 5001-5008

**CI**: GHCR image publishing workflow added

**Time estimate**: 38 hours (dev) + 8 hours (testing/docs) = **46 hours**

---

## Phase 3 (Week 3): Specialized Sites - Edge Cases

**Timeline**: Days 15-21 (Apr 15-21, 2024)
**Goal**: Complete final 5 sites covering i18n, media, anti-bot, alternative entities, streaming

### Sites to Build

#### 3.1 encoding-and-i18n.site (Days 15-16)
**Features**:
- Page 1: ISO-8859-1 encoding (Latin-1) with `Café`, `€` symbol
- Page 2: UTF-8 with Arabic text (RTL)
- Page 3: Hebrew text with bidi markers
- Page 4: Emoji-heavy content 🎉🚀
- Page 5: `Content-Type` mismatch (says UTF-8, is Latin-1)

**Implementation**:
```python
@app.get("/latin1")
async def latin1_page(response: Response):
    response.headers["Content-Type"] = "text/html; charset=ISO-8859-1"
    content = "Café au lait: 5€".encode('latin-1')
    return Response(content=content, media_type="text/html; charset=ISO-8859-1")

@app.get("/arabic")
async def arabic_page():
    return {"content": "مرحبا بك في الموقع"}  # "Welcome to the site"
```

**Time**: 5 hours

**Success criteria**:
- ✅ Latin-1 decoded correctly (no mojibake)
- ✅ RTL text preserved
- ✅ Emojis extracted without corruption
- ✅ Content-Type mismatch handled gracefully

---

#### 3.2 media-and-nonhtml.site (Days 16-17)
**Features**:
- HTML pages linking to:
  - CSS files
  - JavaScript files
  - Images (various formats)
  - Fonts (WOFF2)
- Config flag: `html_only: true` vs `full_resources: true`

**Implementation**:
```python
@app.get("/page-with-assets")
async def page():
    return HTMLResponse("""
    <link rel="stylesheet" href="/style.css">
    <script src="/app.js"></script>
    <img src="/photo.jpg">
    """)

@app.get("/style.css")
async def css():
    return Response("body { color: blue; }", media_type="text/css")
```

**Time**: 4 hours

**Success criteria**:
- ✅ `html_only: true` → Only HTML pages extracted
- ✅ `full_resources: true` → CSS/JS/images recorded (not content-extracted)
- ✅ Mime types correctly identified

---

#### 3.3 anti-bot-lite.site (Days 17-18)
**Features**:
- Rate limiting: 10 requests/minute per IP
- Required headers: `Accept-Language`, `User-Agent`
- Return 429 on burst (>5 requests in 5 seconds)
- Allow session-managed requests (session cookies bypass limits)

**Implementation**:
```python
from collections import defaultdict
import time

request_log = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()

    # Check burst
    recent = [t for t in request_log[client_ip] if now - t < 5]
    if len(recent) >= 5:
        return JSONResponse({"error": "Rate limited"}, status_code=429, headers={"Retry-After": "5"})

    request_log[client_ip].append(now)
    return await call_next(request)
```

**Time**: 6 hours

**Success criteria**:
- ✅ Burst requests (>5 in 5s) return 429
- ✅ Polite crawling respects rate limit
- ✅ Session cookies bypass limit
- ✅ Missing headers cause appropriate errors

---

#### 3.4 jobs-and-offers.site (Days 18-19)
**Features**:
- 50 job postings with JobPosting JSON-LD schema
- 30% use clean HTML (CSS selectors work)
- 70% use messy HTML (need LLM)
- Different fields: `title`, `hiringOrganization`, `datePosted`, `validThrough`, `salary`

**Implementation**:
```python
@app.get("/jobs/{id}")
async def job_detail(id: int):
    job = generate_job(id)

    # 30% clean, 70% messy
    if id % 10 < 3:
        template = "job_clean.html"
    else:
        template = "job_messy.html"

    return templates.TemplateResponse(template, {"job": job})
```

**JSON-LD**:
```json
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "Senior Rust Engineer",
  "hiringOrganization": {"@type": "Organization", "name": "Tech Corp"},
  "datePosted": "2024-04-01",
  "validThrough": "2024-05-01",
  "baseSalary": {"@type": "MonetaryAmount", "value": 150000, "currency": "USD"}
}
```

**Time**: 7 hours

**Success criteria**:
- ✅ All 50 jobs extracted
- ✅ Entity type: `JobPosting` (not Event)
- ✅ Extraction method tracked (selector vs LLM)
- ✅ Salary range correctly parsed

---

#### 3.5 websocket-stream-sink (Days 19-21)
**Features**:
- WebSocket echo server
- Accepts crawl requests via WS
- Streams back NDJSON results
- Supports backpressure (client can pause)

**Implementation**:
```python
from fastapi import WebSocket

@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()

    # Receive crawl config
    config = await websocket.receive_json()

    # Stream results
    for page in crawl_pages(config['urls']):
        await websocket.send_json(page)
        await asyncio.sleep(0.1)  # Throttle

    # Final stats
    await websocket.send_json({"type": "stats", "pages_crawled": 100})
    await websocket.close()
```

**Time**: 8 hours (WebSocket testing is complex)

**Success criteria**:
- ✅ WebSocket connection established
- ✅ NDJSON results streamed
- ✅ Backpressure handled (pause/resume)
- ✅ Final stats event received

---

### Deliverables (End of Week 3)

**Code**: 5 final sites (13 total)

**Complete Suite**:
- All 13 sites containerized
- Full `docker-compose.yml` (ports 5001-5013)
- Complete ground truth (39 files: 3 per site)

**Tests**: 13 E2E test files, >60 assertions total

**CI**: Full integration with RipTide repo

**Documentation**:
- Finalized PLAN.md
- Deployment guide
- Troubleshooting section

**Time estimate**: 30 hours (dev) + 10 hours (final testing/docs) = **40 hours**

---

## Deployment Milestones

### Milestone 1: Local Development (Week 1 End)
- ✅ 3 sites running locally
- ✅ Health checks passing
- ✅ Manual crawl tests work

### Milestone 2: CI Integration (Week 2 End)
- ✅ GitHub Actions workflow in RipTide repo
- ✅ Fixtures submodule added
- ✅ Automated E2E tests running

### Milestone 3: GHCR Publishing (Week 3 End)
- ✅ All 13 images published to `ghcr.io/<org>/riptide-fixture-*`
- ✅ Tagged release `v1.0.0`
- ✅ RipTide CI uses pre-built images (2x faster builds)

### Milestone 4: Staging Deployment (Optional, Week 4)
- ✅ Deploy to Fly.io or Render
- ✅ Configure `fixtures.riptide.dev` subdomain
- ✅ Update RipTide docs with hosted URLs

---

## Integration Points

### RipTide Repository

**Week 1**: Add submodule
```bash
cd riptide-crawler
git submodule add https://github.com/<org>/riptide-fixtures fixtures
```

**Week 2**: Create E2E test suite
```python
# tests/e2e/conftest.py
import pytest
import subprocess

@pytest.fixture(scope="session", autouse=True)
def start_fixtures():
    subprocess.run(["docker-compose", "-f", "fixtures/docker-compose.yml", "up", "-d", "--build"], check=True)
    yield
    subprocess.run(["docker-compose", "-f", "fixtures/docker-compose.yml", "down", "-v"], check=True)
```

**Week 3**: Switch to GHCR images
```yaml
# .github/workflows/e2e.yml
- name: Pull fixture images
  run: docker-compose -f fixtures/docker-compose.yml pull

- name: Start fixtures (no build)
  run: docker-compose -f fixtures/docker-compose.yml up -d
```

### Validation Criteria

Each site must pass:
1. **Health check** (`curl http://localhost:5xxx/` returns 200)
2. **Ground truth match** (crawl output matches expected.jsonl within 5% variance)
3. **Performance** (crawl completes in <30s for sites with <200 pages)
4. **Isolation** (can run concurrently without conflicts)

---

## Maintenance Plan

### Post-Launch (Ongoing)

**Monthly**:
- Run full E2E suite
- Update dependencies (Faker, FastAPI)
- Verify GHCR images still pull

**Per RipTide Release**:
- Regenerate ground truth if extraction changes
- Update site complexity if new features added (e.g., new schema types)

**On Bug Reports**:
- Add regression test to relevant site
- Update ground truth
- Tag new fixture version

### Versioning Strategy

**Semantic versioning**:
- **Major** (1.0.0 → 2.0.0): Breaking changes to site structure/URLs
- **Minor** (1.0.0 → 1.1.0): New sites added, backward-compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes, content updates

**Example**:
- `v0.1.0` - Week 1 (3 sites)
- `v0.2.0` - Week 2 (8 sites)
- `v1.0.0` - Week 3 (13 sites, production-ready)
- `v1.1.0` - Future (add site #14 for GraphQL testing)

### Deprecation Policy

If a site needs breaking changes:
1. Mark as deprecated in `PLAN.md`
2. Keep running for 1 minor version
3. Remove in next major version
4. Update RipTide tests to use new site

---

## Risk Mitigation

### Potential Issues

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM quota exhausted | Tests fail | Use LLM mock in CI, real LLM in staging only |
| Docker build slow | CI timeout | Publish GHCR images, use in CI |
| Ground truth drift | False failures | Automated regeneration script, version control |
| Port conflicts | Local dev breaks | Use `.env` for port overrides |
| Faker data changes | Non-deterministic | Pin Faker version, use fixed seed |

### Contingency Plans

**If behind schedule**:
- Week 1: Ship 2 sites instead of 3 (drop robots-sitemaps)
- Week 2: Skip WebSocket site (defer to v1.1.0)
- Week 3: Deploy locally only (skip GHCR publishing)

**If blockers occur**:
- **LLM integration complex**: Use placeholder extraction method, add real LLM in v1.1.0
- **WebSocket tricky**: Replace with SSE streaming test
- **CI flaky**: Add retry logic, increase timeouts

---

## Success Metrics

### End of Week 3

- ✅ **13 sites** running and health-checked
- ✅ **39 ground truth files** committed
- ✅ **13 E2E test files** passing in CI
- ✅ **100% feature coverage** (all RipTide capabilities tested)
- ✅ **<5 minute setup** for new developers
- ✅ **<10 minute CI run** for full E2E suite
- ✅ **GHCR images** published and versioned

### Adoption Metrics (Month 1)

- 5+ developers run fixtures locally
- 0 false-positive test failures
- 2+ external contributions (new sites or improvements)
- 95%+ uptime for staging deployment

---

## Next Steps

**Week 0 (Prep)**:
1. Create `riptide-fixtures` repository
2. Set up Docker Compose skeleton
3. Create first site template (happy-path)

**Day 1**:
- [ ] Implement happy-path.site
- [ ] Generate ground truth
- [ ] Write first E2E test

**Day 7 Review**:
- Assess progress vs. Week 1 plan
- Adjust Week 2 scope if needed

**Day 21 Launch**:
- Publish v1.0.0 release
- Announce in RipTide repo
- Update documentation

---

**For questions or adjustments to this roadmap, see [PLAN.md](./PLAN.md) for technical details.**
# Test Sites - Shortcuts & Ready-to-Use Resources

**Quick reference for existing resources that speed up development by 60-75%**

---

## 🚀 Ready-to-Use Public Test Sites

Instead of building custom sites, you can use these existing public resources:

### 1. **httpbin.org** - HTTP Testing Service
**Use for**: slowpoke-and-retries.site, redirects-canonical.site
- **URL**: https://httpbin.org
- **Features**: Delays, redirects, status codes, auth, headers, cookies
- **Examples**:
  - Delays: `httpbin.org/delay/3`
  - 429 errors: `httpbin.org/status/429`
  - Redirects: `httpbin.org/redirect/5`
- **Coverage**: 85-90% of HTTP behavior testing needs
- **Setup**: Zero - use as-is

### 2. **toscrape.com Sites** - Scraping Sandboxes
**Use for**: happy-path.site reference
- **Books**: http://books.toscrape.com
- **Quotes**: http://quotes.toscrape.com
- **Features**: Pagination, search, categories, clean HTML
- **Coverage**: Great for basic crawling patterns
- **Setup**: Zero - publicly hosted

### 3. **Wikipedia** - Stable Real Site
**Use for**: happy-path.site baseline
- **URL**: https://en.wikipedia.org
- **Features**: Stable HTML, good structure, JSON-LD
- **Coverage**: Perfect for baseline crawling
- **Setup**: Zero - use selectively

---

## 📦 FastAPI Templates (60-75% Time Savings)

### 1. **FastAPI Full Stack Template** ⭐ PRIMARY CHOICE
**Repository**: https://github.com/tiangolo/full-stack-fastapi-template
- **Stars**: 38,700+ ⭐
- **Maintained**: Active (Feb 2025)
- **What You Get**:
  - FastAPI backend + React frontend
  - PostgreSQL + SQLModel ORM
  - Docker Compose configuration
  - JWT authentication
  - Admin dashboard
  - GitHub Actions CI/CD
  - Traefik proxy with automatic HTTPS
- **Setup Time**: 30 minutes
- **Use For**: All 13 test sites as base
- **Time Savings**: 2-3 days per site

**Quick Start**:
```bash
# Clone template
git clone https://github.com/tiangolo/full-stack-fastapi-template
cd full-stack-fastapi-template

# Customize for your site
cp .env.example .env
# Edit PROJECT_NAME, etc.

# Run
docker-compose up
```

### 2. **FastAPI + Jinja2 Boilerplate** (For HTML-heavy sites)
**Repository**: https://github.com/Mateko/FastAPI-boilerplate
- **Tech Stack**: FastAPI, Jinja2, TailwindCSS
- **What You Get**: HTML templating, CSS framework
- **Use For**: Sites with complex HTML (happy-path, selectors-vs-llm)
- **Setup Time**: 15 minutes

---

## 🎲 Faker.js - Deterministic Test Data

**Repository**: https://github.com/faker-js/faker
- **Stars**: 14,600+ ⭐
- **Setup**: `npm install @faker-js/faker`
- **Use For**: ALL sites - generate realistic data

**Example** (Deterministic):
```javascript
import { faker } from '@faker-js/faker';

// Seeded for reproducibility
faker.seed(42);

const events = Array.from({ length: 100 }, (_, i) => ({
  id: i + 1,
  name: faker.company.name() + ' Event',
  date: faker.date.future(),
  location: faker.location.city(),
  description: faker.lorem.paragraph()
}));
```

**Python Alternative**:
```python
from faker import Faker
fake = Faker()
Faker.seed(42)  # Deterministic

events = [
    {
        'id': i,
        'name': fake.company() + ' Event',
        'date': fake.future_date(),
        'location': fake.city()
    }
    for i in range(100)
]
```

---

## 🐳 Docker Compose Examples

### All 13 Sites - Complete docker-compose.yml

From FastAPI Full Stack Template:
```yaml
services:
  # Site 1: happy-path
  happy-path:
    build: ./sites/happy-path.site
    ports:
      - "5001:8000"
    environment:
      - FIXTURE_SEED=42
    volumes:
      - ./sites/happy-path.site:/app

  # Site 2: selectors-vs-llm
  selectors-llm:
    build: ./sites/selectors-vs-llm.site
    ports:
      - "5002:8000"
    environment:
      - FIXTURE_SEED=42

  # ... repeat for all 13 sites
```

---

## 🔥 Hosting Shortcuts

### Option 1: Hetzner + One-Click Coolify Install
**Cost**: €3.49/month
**Setup**: 10 minutes

```bash
# 1. Create Hetzner VPS (via web UI)
# 2. SSH into VPS
ssh root@your-vps-ip

# 3. Install Coolify (one command)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# 4. Access Coolify UI
# http://your-vps-ip:8000
```

### Option 2: Google Cloud Run (Free Tier)
**Cost**: $0
**Setup**: 5 minutes

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Deploy one site
gcloud run deploy happy-path \
  --source ./sites/happy-path.site \
  --allow-unauthenticated \
  --region us-central1

# Get URL (automatic):
# https://happy-path-abc123.run.app
```

---

## 📚 Pre-Built Site Generators

### JSON-LD Generator (For happy-path, jobs-and-offers)
```python
from datetime import datetime

def generate_event_jsonld(event):
    return {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event['name'],
        "startDate": event['date'].isoformat(),
        "location": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": event['location']
            }
        }
    }
```

### Pagination Generator
```python
def paginate_items(items, page=1, per_page=20):
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': len(items),
        'pages': (len(items) + per_page - 1) // per_page
    }
```

---

## 🎯 Site-by-Site Shortcuts

| Site | Shortcut | Time Saved |
|------|----------|-----------|
| **happy-path** | FastAPI + Faker + Wikipedia reference | 8h → 2h |
| **selectors-vs-llm** | FastAPI + varied HTML templates | 10h → 3h |
| **static-vs-headless** | FastAPI + JS-gated content | 8h → 3h |
| **pdfs-and-binaries** | PyPDF2 + FastAPI | 5h → 2h |
| **redirects-canonical** | **httpbin.org** (use as-is) | 6h → 0.5h |
| **robots-and-sitemaps** | FastAPI + XML templates | 6h → 2h |
| **slowpoke-and-retries** | **httpbin.org/delay** + FastAPI | 6h → 1h |
| **auth-and-session** | FastAPI Full Stack (has auth) | 12h → 3h |
| **encoding-and-i18n** | Faker locales + FastAPI | 8h → 3h |
| **media-and-nonhtml** | httpbin.org + local files | 4h → 1h |
| **anti-bot-lite** | FastAPI + SlowAPI middleware | 5h → 2h |
| **jobs-and-offers** | FastAPI + JobPosting JSON-LD | 6h → 2h |
| **websocket-stream-sink** | FastAPI WebSocket example | 6h → 2h |

**Total Time Savings**: ~90 hours → ~25 hours (72% faster)

---

## 📖 Complete Setup Example

### Example: Build happy-path.site in 2 hours

```bash
# 1. Clone FastAPI template (5 min)
git clone https://github.com/tiangolo/full-stack-fastapi-template happy-path-site
cd happy-path-site

# 2. Simplify (remove frontend, keep backend) (10 min)
rm -rf frontend/
rm docker-compose.override.yml

# 3. Add Faker for data generation (5 min)
# Edit backend/app/main.py
from faker import Faker
fake = Faker()
Faker.seed(42)

@app.get("/events")
def list_events():
    events = [create_fake_event() for _ in range(100)]
    return {"events": events}

# 4. Add JSON-LD (15 min)
# Add schema.org structured data to templates

# 5. Add sitemap.xml (10 min)
@app.get("/sitemap.xml")
def sitemap():
    return generate_sitemap()

# 6. Test locally (5 min)
docker-compose up

# 7. Deploy to Cloud Run (10 min)
gcloud run deploy happy-path --source .

# Total: ~60 minutes + 60 min testing/polish = 2 hours
```

---

## 🔗 All Key Links

### Templates
- FastAPI Full Stack: https://github.com/tiangolo/full-stack-fastapi-template
- FastAPI + Jinja2: https://github.com/Mateko/FastAPI-boilerplate
- Faker.js: https://github.com/faker-js/faker
- Python Faker: https://github.com/joke2k/faker

### Public Test Sites
- httpbin: https://httpbin.org
- Books to Scrape: http://books.toscrape.com
- Quotes to Scrape: http://quotes.toscrape.com

### Hosting
- Hetzner Cloud: https://www.hetzner.com/cloud
- Coolify Install: https://coolify.io/docs/installation
- Google Cloud Run: https://cloud.google.com/run/docs

### Tools
- sslip.io: Wildcard DNS (no signup)
- nip.io: Alternative wildcard DNS

---

## ✨ Bottom Line

**Don't build from scratch**:
- Use httpbin.org for HTTP behavior testing
- Start with FastAPI Full Stack Template
- Generate data with Faker (seeded)
- Deploy to Cloud Run (free) or Hetzner ($4/month)

**Result**: Build all 13 sites in ~25 hours instead of 90+ hours.
