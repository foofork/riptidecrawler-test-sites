# 🧪 RipTide Test Sites

A **containerized multi-site testing platform** featuring **13 independent FastAPI web apps** for evaluating web crawling, data extraction, and validation across real-world scenarios.

---

## 🚀 Quick Start (5 Minutes)

```bash
# Clone the repository
git clone <repo-url>
cd riptide-test-sites

# Start all 13 sites
docker compose up -d

# Verify all sites are healthy
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

## 📘 Overview

**RipTide Test Sites** provides a reproducible environment for testing and benchmarking web crawlers, extractors, and agents across 13 deterministic site types.

**Highlights**

* ✅ Deterministic data generation (`Faker.seed = 42`)
* ✅ 13 fully isolated Docker containers
* ✅ Diverse coverage — from HTML and JS rendering to WebSockets
* ✅ Built-in health checks
* ✅ Startup in under 10 seconds
* ✅ No external APIs or databases required

> 💡 A **self-contained testbed for any web crawler**.

---

## 🧩 Integration

RipTide Test Sites is **framework-agnostic**.
It was designed to validate [**RipTideCrawler**](https://github.com/foofork/riptidecrawler) but works seamlessly with **any crawler or agent system**.

See the [**Integration Guide**](docs/INTEGRATION_GUIDE.md) for ready-to-run examples in **Rust, Python, and Node.js**.

**Covers all key crawling & extraction patterns:**

* Static vs. headless rendering
* CSS selectors vs. LLM-based extraction
* Robots.txt & sitemap compliance
* PDF and binary file handling
* Auth/session persistence
* Rate-limiting and retry logic
* Streaming via NDJSON, SSE, and WebSocket
* Multi-language and encoding edge cases

---

## 🏗️ Architecture

Each test site is an independent **FastAPI** app packaged in Docker, exposing both REST and WebSocket interfaces.

```
┌──────────────────────────────────────────────────────────┐
│       Docker Compose Network (bridge)                    │
├──────────────────────────────────────────────────────────┤
│  Site1 ... Site13  →  FastAPI apps on ports 5001–5013    │
└──────────────────────────────────────────────────────────┘
```

**Stack**

* Python 3.11+
* FastAPI 0.104+
* Faker 20.0+
* Jinja2
* Docker & Docker Compose

---

## 📚 Site Catalog

### Phase 1 — Foundation

| # | Site                         | Port | Purpose              | Highlights                      |
| - | ---------------------------- | ---- | -------------------- | ------------------------------- |
| 1 | **happy-path.site**          | 5001 | Baseline crawling    | Simple HTML + pagination        |
| 2 | **redirects-canonical.site** | 5002 | URL normalization    | 301/302 chains + canonical tags |
| 3 | **robots-and-sitemaps.site** | 5003 | Standards compliance | robots.txt + XML sitemaps       |

### Phase 2 — Intermediate

| # | Site                          | Port | Purpose             | Highlights                   |
| - | ----------------------------- | ---- | ------------------- | ---------------------------- |
| 4 | **slowpoke-and-retries.site** | 5004 | Resilience testing  | Delays, rate limits, retries |
| 5 | **selectors-vs-llm.site**     | 5005 | Extraction methods  | CSS vs. LLM extraction       |
| 6 | **static-vs-headless.site**   | 5006 | Rendering detection | JS-rendered content          |
| 7 | **pdfs-and-binaries.site**    | 5007 | Binary handling     | PDFs and images              |
| 8 | **auth-and-session.site**     | 5008 | Authentication      | Login + sessions             |

### Phase 3 — Advanced

| #  | Site                       | Port | Purpose              | Highlights                    |
| -- | -------------------------- | ---- | -------------------- | ----------------------------- |
| 9  | **encoding-and-i18n.site** | 5009 | Internationalization | Multiple encodings + RTL text |
| 10 | **media-and-nonhtml.site** | 5010 | Content types        | JSON, XML, CSV, OpenGraph     |
| 11 | **anti-bot-lite.site**     | 5011 | Bot detection        | UA checks, CAPTCHA sim        |
| 12 | **jobs-and-offers.site**   | 5012 | Schema.org tests     | JobPosting JSON-LD            |
| 13 | **websocket-stream-sink**  | 5013 | Real-time streaming  | NDJSON via WebSocket          |

---

## 🧪 Testing

### Manual

```bash
curl http://localhost:5001/
curl -L http://localhost:5002/redirect-chain/3
curl http://localhost:5003/robots.txt
time curl http://localhost:5004/slow-page
wscat -c ws://localhost:5013/ws/crawl
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

## ⚙️ Development Workflow

**Start, stop, and restart:**

```bash
docker compose up -d             # All sites
docker compose up -d happy-path  # One site
docker compose restart jobs-and-offers
docker compose down              # Stop all
```

**Health & Logs**

```bash
for port in {5001..5013}; do curl -s http://localhost:$port/health | jq; done
docker compose logs -f selectors-vs-llm
```

Expected `/health`:

```json
{ "status": "healthy", "site": "happy-path", "uptime": 3600, "data_generated": true }
```

---

## 🔧 Configuration

All sites share these environment variables:

```bash
FAKER_SEED=42
SITE_NAME=happy-path
PORT=8000
DATA_SIZE=100
DEBUG=true
```

Customize via `docker-compose.yml`:

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

| Problem                      | Solution                                                  |
| ---------------------------- | --------------------------------------------------------- |
| **Sites not starting**       | Check `docker info`, rebuild, then `docker compose up -d` |
| **Port conflicts**           | Edit `ports:` mapping in Compose                          |
| **Health check fails**       | Wait 15s → `docker compose logs happy-path`               |
| **High CPU/memory**          | Add `cpus: '0.5'`, `memory: 512M` limits                  |
| **WebSocket not connecting** | Use `wscat`, disable reverse proxies/firewalls            |

---

## 📄 Documentation

* ⭐ [Integration Guide](docs/INTEGRATION_GUIDE.md)
* [Quick Reference](docs/QUICK_REFERENCE.md)
* [Architecture](docs/architecture.md)
* [Deployment Guide](docs/deployment-guide.md)
* [Development Guide](docs/development.md)
* [Testing Guide](docs/testing.md)
* [Ground Truth Reference](docs/GROUND_TRUTH_QUICK_REFERENCE.md)
* [Roadmap](docs/ROADMAP.md)

---

## 🎯 Use Cases

* **Crawler development** — redirects, robots.txt, rate-limits
* **Extraction validation** — LLM vs selector-based, messy HTML
* **Edge case handling** — encodings, binaries, auth, JS rendering
* **Benchmarking** — performance across formats and locales

---

## 🤝 Contributing

1. Add a new directory under `sites/`
2. Include a minimal FastAPI app with `/` and `/health`
3. Update `docker-compose.yml`
4. Use `Faker.seed(42)` for deterministic output

---

## 🔐 Security

* Isolated Docker containers
* Stateless in-memory data
* No external databases or APIs
* Safe for CI/CD and sandbox use

---

## 📊 Performance Snapshot

| Metric           | Value                   |
| ---------------- | ----------------------- |
| Startup (all 13) | 10–15 s                 |
| Memory           | 50–100 MB per container |
| CPU              | Low (FastAPI async)     |
| Disk             | ~200 MB total           |
| Network          | Local bridge            |

---

## 📝 License

[MIT License](LICENSE)

---

## ❤️ Acknowledgments

Built with [FastAPI](https://fastapi.tiangolo.com/), [Faker](https://faker.readthedocs.io/), [Docker](https://www.docker.com/), and [Jinja2](https://jinja.palletsprojects.com/).

> **Made with ❤️ for reliable web crawling and extraction testing.**