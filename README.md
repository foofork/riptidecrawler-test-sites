# RipTide Test Sites

A **containerized multi-site testing platform** with 13 independent web applications for evaluating web crawling, data extraction, and validation capabilities across diverse scenarios.

---

## 🚀 Quick Start (5 Minutes)

```bash
# Clone repository
git clone <repo-url>
cd riptide-test-sites

# Start all 13 sites
docker compose up -d

# Verify all sites are running
for port in {5001..5013}; do
  curl -s http://localhost:$port/health | jq
done

# View logs
docker compose logs -f
```

**Access Sites**

| Site                  | URL                                            |
| --------------------- | ---------------------------------------------- |
| Happy Path            | [http://localhost:5001](http://localhost:5001) |
| Redirects & Canonical | [http://localhost:5002](http://localhost:5002) |
| Robots & Sitemaps     | [http://localhost:5003](http://localhost:5003) |
| Slowpoke & Retries    | [http://localhost:5004](http://localhost:5004) |
| Selectors vs LLM      | [http://localhost:5005](http://localhost:5005) |
| Static vs Headless    | [http://localhost:5006](http://localhost:5006) |
| PDFs & Binaries       | [http://localhost:5007](http://localhost:5007) |
| Auth & Session        | [http://localhost:5008](http://localhost:5008) |
| Encoding & i18n       | [http://localhost:5009](http://localhost:5009) |
| Media & Non-HTML      | [http://localhost:5010](http://localhost:5010) |
| Anti-Bot Lite         | [http://localhost:5011](http://localhost:5011) |
| Jobs & Offers         | [http://localhost:5012](http://localhost:5012) |
| WebSocket Stream      | [http://localhost:5013](http://localhost:5013) |

---

## 📋 Overview

**RipTide Test Sites** provides 13 specialized web apps for testing web crawlers and extractors.
All data is **deterministically generated** (Faker seed = 42) for fully reproducible runs.

**Key Features**

* ✅ Deterministic data generation
* ✅ Isolated Docker containers
* ✅ Comprehensive scenarios (from HTML to WebSocket streams)
* ✅ Built-in health checks
* ✅ Fast startup (~10 seconds)
* ✅ No external APIs or DBs required


---

### 🧩 Relationship to RipTideCrawler

RipTide Test Sites is an **agnostic** testing platform for web crawlers, extractors, and agents — but it was **originally built to validate** and **benchmark** the full feature set of [**RipTideCrawler**](https://github.com/foofork/riptidecrawler).

It covers 100 % of common crawling and extraction cases exercised by RipTideCrawler, including:

* WASM-based selector extraction
* LLM fallback extraction
* Static vs headless routing
* PDF and binary handling
* Robots/sitemap compliance
* Real-time NDJSON / SSE / WebSocket streaming
* Job storage + pagination
* Multi-language and encoding edge cases
* Auth / session / rate-limit resilience

> 💡 A **“testbed for any web crawler”**.

---

## 🏗️ Architecture

Each site is a **FastAPI** application running in Docker with:

* Deterministic Faker-generated data (seed = 42)
* Semantic HTML + structured metadata
* Health check endpoints
* REST and WebSocket interfaces

```
┌─────────────────────────────────────────────────────────┐
│              Docker Compose Network (bridge)             │
├─────────────────────────────────────────────────────────┤
│  Site1 ... Site13  →  FastAPI apps on ports 5001–5013    │
└─────────────────────────────────────────────────────────┘
```

**Stack**

* Python 3.11+
* FastAPI 0.104+
* Faker 20.0+
* Jinja2
* Docker & Docker Compose

---

## 📊 Site Catalog

### Phase 1 — Foundation

| # | Site                         | Port | Purpose              | Highlights                           |
| - | ---------------------------- | ---- | -------------------- | ------------------------------------ |
| 1 | **happy-path.site**          | 5001 | Baseline crawling    | Simple HTML + pagination (100 items) |
| 2 | **redirects-canonical.site** | 5002 | URL normalization    | 301/302 chains + canonical tags      |
| 3 | **robots-and-sitemaps.site** | 5003 | Standards compliance | robots.txt + XML sitemaps            |

### Phase 2 — Intermediate

| # | Site                          | Port | Purpose             | Highlights                   |
| - | ----------------------------- | ---- | ------------------- | ---------------------------- |
| 4 | **slowpoke-and-retries.site** | 5004 | Resilience testing  | Delays, rate limits, retries |
| 5 | **selectors-vs-llm.site**     | 5005 | Extraction methods  | CSS vs LLM comparison        |
| 6 | **static-vs-headless.site**   | 5006 | Rendering detection | JS-rendered content          |
| 7 | **pdfs-and-binaries.site**    | 5007 | Binary handling     | PDF + image serving          |
| 8 | **auth-and-session.site**     | 5008 | Authentication      | Login + session flows        |

### Phase 3 — Advanced

| #  | Site                       | Port | Purpose              | Highlights                      |
| -- | -------------------------- | ---- | -------------------- | ------------------------------- |
| 9  | **encoding-and-i18n.site** | 5009 | Internationalization | Multiple encodings + RTL        |
| 10 | **media-and-nonhtml.site** | 5010 | Content types        | JSON, XML, CSV, OpenGraph       |
| 11 | **anti-bot-lite.site**     | 5011 | Bot detection        | User-Agent checks, CAPTCHA sim  |
| 12 | **jobs-and-offers.site**   | 5012 | Schema.org tests     | JobPosting JSON-LD + messy HTML |
| 13 | **websocket-stream-sink**  | 5013 | Real-time streams    | NDJSON WebSocket output         |

---

## 🛠️ Development Workflow

### Site Control

```bash
docker compose up -d            # Start all sites
docker compose up -d happy-path # Start one site
docker compose restart jobs-and-offers
docker compose down             # Stop all
```

### Logs & Health

```bash
docker compose logs -f selectors-vs-llm
for port in {5001..5013}; do
  curl -s http://localhost:$port/health | jq
done
```

Expected `/health` response:

```json
{ "status": "healthy", "site": "happy-path", "uptime": 3600, "data_generated": true }
```

---

## 🧪 Testing

### Manual Checks

Use `curl`, `jq`, or `wscat` to test behavior:

```bash
curl http://localhost:5001/                     # simple HTML
curl -L http://localhost:5002/redirect-chain/3  # redirect test
curl http://localhost:5003/robots.txt
time curl http://localhost:5004/slow-page
wscat -c ws://localhost:5013/ws/crawl           # WebSocket test
```

### Automated (pytest-style)

```python
import requests, websocket, json

def test_happy_path():
    r = requests.get("http://localhost:5001/health")
    assert r.ok and r.json()["status"] == "healthy"

def test_jobs_schema():
    jobs = requests.get("http://localhost:5012/api/jobs").json()
    assert jobs and jobs[0]["@type"] == "JobPosting"

def test_websocket_stream():
    ws = websocket.create_connection("ws://localhost:5013/ws/crawl")
    ws.send('{"action":"start","pages":5}')
    assert "page" in json.loads(ws.recv())
    ws.close()
```

---

## 📁 Repository Layout

```
riptide-test-sites/
├── docker-compose.yml
├── sites/
│   ├── happy-path.site/
│   ├── redirects-canonical.site/
│   ├── robots-and-sitemaps.site/
│   ├── slowpoke-and-retries.site/
│   ├── selectors-vs-llm.site/
│   ├── static-vs-headless.site/
│   ├── pdfs-and-binaries.site/
│   ├── auth-and-session.site/
│   ├── encoding-and-i18n.site/
│   ├── media-and-nonhtml.site/
│   ├── anti-bot-lite.site/
│   ├── jobs-and-offers.site/
│   └── websocket-stream-sink/
├── docs/
│   ├── QUICK_REFERENCE.md
│   ├── GROUND_TRUTH_QUICK_REFERENCE.md
│   ├── ROADMAP.md
│   ├── architecture.md
│   ├── deployment-guide.md
│   ├── development.md
│   ├── testing.md
│   └── archive/ (historical reports)
└── scripts/
    ├── health_check.sh
    └── validate_all.sh
```

---

## 🚢 Deployment Options

| Environment                        | Cost       | Setup Time | Notes                         |
| ---------------------------------- | ---------- | ---------- | ----------------------------- |
| **Local (default)**                | Free       | 5 min      | `docker compose up -d`        |
| **Docker Swarm / K8s**             | Varies     | 1–2 h      | Auto-scaling, health checks   |
| **Cloud Run / ECS / ACI / Heroku** | Free–Low   | 30–60 min  | Use container deploy workflow |
| **VPS (Compose)**                  | $5–10 / mo | 30 min     | DigitalOcean, Hetzner, etc.   |

---

## 🔧 Configuration

All sites accept:

```bash
FAKER_SEED=42     # Deterministic data
SITE_NAME=happy-path
PORT=8000
DATA_SIZE=100
DEBUG=true
```

To customize:

```yaml
environment:
  - DATA_SIZE=200
ports:
  - "6001:8000"
```

Add a custom site:

```yaml
custom-site:
  build: ./sites/custom-site
  ports: ["5014:8000"]
  environment:
    - SITE_NAME=custom-site
    - FAKER_SEED=42
```

---

## 🐛 Troubleshooting

| Issue                  | Fix                                              |
| ---------------------- | ------------------------------------------------ |
| **Sites won’t start**  | `docker info` → rebuild → `docker compose up -d` |
| **Port conflicts**     | Change `ports:` mapping                          |
| **Health check fails** | Wait 15 s → `docker compose logs happy-path`     |
| **High CPU/mem**       | Limit in Compose: `cpus: '0.5'`, `memory: 512M`  |
| **WebSocket issues**   | Test with `wscat`, check proxies/firewalls       |

---

## 📚 Docs

* [Quick Reference](docs/QUICK_REFERENCE.md)
* [Architecture](docs/architecture.md)
* [Deployment Guide](docs/deployment-guide.md)
* [Development Guide](docs/development.md)
* [Testing Guide](docs/testing.md)
* [Ground Truth Reference](docs/GROUND_TRUTH_QUICK_REFERENCE.md)
* [Roadmap](docs/ROADMAP.md)

---

## 🎯 Use Cases

* **Crawler development:** HTML crawl, redirects, robots, rate limits
* **Extraction testing:** CSS vs LLM, JSON-LD, messy HTML, OpenGraph
* **Edge cases:** encodings, binaries, auth, JS rendering, WebSockets
* **Benchmarking:** performance across content types and encodings

---

## 🤝 Contributing

1. Create a new site directory under `sites/`.
2. Add a simple FastAPI app with `/` and `/health`.
3. Update `docker-compose.yml`.
4. Keep `Faker.seed(42)` for reproducibility.

---

## 🔐 Security

* Isolated Docker containers
* No external DBs
* Stateless, in-memory data
* Test-only auth credentials
* Safe for CI/CD environments

---

## 📊 Performance Snapshot

| Metric           | Value                    |
| ---------------- | ------------------------ |
| Startup (all 13) | 10–15 s                  |
| Memory           | ~50–100 MB per container |
| CPU              | Low (FastAPI async)      |
| Disk             | ~200 MB total            |
| Network          | Local bridge             |

---

## 📝 License

[MIT License] —or your chosen license.

---

## 🙏 Acknowledgments

Built with [FastAPI](https://fastapi.tiangolo.com/), [Faker](https://faker.readthedocs.io/), [Docker](https://www.docker.com/), and [Jinja2](https://jinja.palletsprojects.com/).

---

**Made with ❤️ for reliable web-crawling and data-extraction testing.**

---

Would you like me to tailor this version for your **`riptide-fixtures`** repo specifically (with fewer phase references and tighter alignment to the sites we generated), or keep it general for the full 13-site suite?
