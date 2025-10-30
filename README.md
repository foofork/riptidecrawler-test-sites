# RipTide Test Sites

A containerized multi-site testing platform consisting of 13 independent web applications designed to test web crawling, data extraction, and validation capabilities across diverse scenarios.

## 🚀 Quick Start (5 Minutes)

```bash
# Clone repository
git clone <repo-url>
cd riptide-test-sites

# Start all 13 sites
docker-compose up -d

# Verify all sites are running
for port in 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010 5011 5012 5013
do
  curl -s http://localhost:$port/health | jq
done

# View logs
docker-compose logs -f
```

**Access Sites:**
- Happy Path: http://localhost:5001
- Redirects & Canonical: http://localhost:5002
- Robots & Sitemaps: http://localhost:5003
- Slowpoke & Retries: http://localhost:5004
- Selectors vs LLM: http://localhost:5005
- Static vs Headless: http://localhost:5006
- PDFs & Binaries: http://localhost:5007
- Auth & Session: http://localhost:5008
- Encoding & i18n: http://localhost:5009
- Media & Non-HTML: http://localhost:5010
- Anti-Bot Lite: http://localhost:5011
- Jobs & Offers: http://localhost:5012
- WebSocket Stream: http://localhost:5013

## 📋 What This Is

RipTide Test Sites provides **13 specialized web applications** for testing various web crawling scenarios, edge cases, and extraction methods. Each site uses **deterministic data generation** (Faker with seed=42) to ensure reproducible results across test runs.

### Key Features

✅ **Deterministic Data** - Same data every time (seed=42)
✅ **Isolated Containers** - Each site runs independently
✅ **Comprehensive Scenarios** - From simple HTML to WebSocket streaming
✅ **Health Monitoring** - Built-in health checks for all sites
✅ **Fast Startup** - All 13 sites start in ~10 seconds
✅ **Zero Dependencies** - No external APIs or databases needed

## 🏗️ Architecture

Each site is a **FastAPI application** running in Docker with:
- Deterministic data generation (Faker seed=42)
- Semantic HTML with structured metadata
- Health check endpoints
- RESTful APIs for testing
- WebSocket support (where applicable)

```
┌─────────────────────────────────────────────────────────┐
│              Docker Compose Network (bridge)             │
├─────────────────────────────────────────────────────────┤
│  Site 1    Site 2    Site 3    ...    Site 12   Site 13 │
│  :5001     :5002     :5003            :5012     :5013    │
│ [FastAPI] [FastAPI] [FastAPI]  ...  [FastAPI]  [FastAPI]│
└─────────────────────────────────────────────────────────┘
```

**Technology Stack:**
- FastAPI 0.104+ (async web framework)
- Python 3.11+
- Faker 20.0+ (deterministic data)
- Jinja2 (templating)
- Docker + Docker Compose

## 📊 Site Descriptions

### Phase 1: Foundation Sites

| # | Site Name | Port | Purpose | Key Features |
|---|-----------|------|---------|--------------|
| 1 | **happy-path.site** | 5001 | Baseline crawling test | Simple HTML, CSS selectors, pagination (100 items) |
| 2 | **redirects-canonical.site** | 5002 | URL normalization | 301/302 redirects, canonical tags, redirect chains (50 items) |
| 3 | **robots-and-sitemaps.site** | 5003 | Standards compliance | robots.txt, XML sitemaps, crawl rules (150 items) |

### Phase 2: Intermediate Sites

| # | Site Name | Port | Purpose | Key Features |
|---|-----------|------|---------|--------------|
| 4 | **slowpoke-and-retries.site** | 5004 | Resilience testing | Artificial delays, rate limiting, retry logic |
| 5 | **selectors-vs-llm.site** | 5005 | Extraction methods | CSS selectors vs LLM extraction comparison (10 items) |
| 6 | **static-vs-headless.site** | 5006 | Rendering detection | JavaScript-rendered content detection (20 items) |
| 7 | **pdfs-and-binaries.site** | 5007 | Binary file handling | PDF generation, image serving, file downloads |
| 8 | **auth-and-session.site** | 5008 | Authentication | Login flows, session management, protected routes |

### Phase 3: Advanced Sites

| # | Site Name | Port | Purpose | Key Features |
|---|-----------|------|---------|--------------|
| 9 | **encoding-and-i18n.site** | 5009 | Internationalization | 10+ encodings, 20+ languages, RTL support |
| 10 | **media-and-nonhtml.site** | 5010 | Content types | JSON, XML, CSV, OpenGraph, Twitter Cards |
| 11 | **anti-bot-lite.site** | 5011 | Bot detection | User-Agent validation, rate limiting, CAPTCHA simulation |
| 12 | **jobs-and-offers.site** | 5012 | Schema.org metadata | JobPosting JSON-LD, 70% messy HTML, 30% clean HTML (50 jobs) |
| 13 | **websocket-stream-sink** | 5013 | Real-time streaming | WebSocket NDJSON streaming, backpressure handling |

## 🛠️ Development Workflow

### Start/Stop Sites

```bash
# Start all sites
docker-compose up -d

# Start specific site
docker-compose up -d happy-path

# Stop all sites
docker-compose down

# Restart all sites
docker-compose restart

# Restart specific site
docker-compose restart jobs-and-offers
```

### View Logs

```bash
# View all logs (follow mode)
docker-compose logs -f

# View logs for specific site
docker-compose logs -f selectors-vs-llm

# View last 50 lines
docker-compose logs --tail=50 websocket-stream-sink
```

### Health Checks

```bash
# Check all sites
for port in {5001..5013}; do
  echo "Checking port $port..."
  curl -s http://localhost:$port/health | jq
done

# Check specific site
curl http://localhost:5001/health

# Expected response:
# {
#   "status": "healthy",
#   "site": "happy-path",
#   "uptime": 3600,
#   "data_generated": true
# }
```

### Testing

```bash
# Test simple HTML crawling
curl http://localhost:5001/

# Test API endpoints
curl http://localhost:5012/api/jobs | jq

# Test WebSocket (requires wscat: npm install -g wscat)
wscat -c ws://localhost:5013/ws/crawl

# Test PDF generation
curl -O http://localhost:5007/api/generate-pdf/report

# Test authentication
curl -X POST http://localhost:5008/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

### Resource Monitoring

```bash
# Show container status
docker-compose ps

# Show resource usage
docker stats $(docker-compose ps -q)

# Check disk usage
docker system df
```

## 🧪 Testing Strategy

### Manual Testing

Each site provides specific endpoints for testing:

```bash
# Happy Path - Basic crawling
curl http://localhost:5001/ | grep -c "<article>"

# Redirects - Test redirect chains
curl -L http://localhost:5002/redirect-chain/3

# Robots.txt - Verify crawl rules
curl http://localhost:5003/robots.txt

# Slowpoke - Test timeout handling
time curl http://localhost:5004/slow-page

# Selectors vs LLM - Compare extraction
curl http://localhost:5005/api/extract-comparison

# Static vs Headless - Check JS rendering
curl http://localhost:5006/js-rendered-content

# PDFs - Download binary
curl -O http://localhost:5007/static/pdfs/sample.pdf

# Auth - Test login flow
curl -c cookies.txt -X POST http://localhost:5008/api/login \
  -d "username=demo&password=demo123"

# Encoding - Test character sets
curl http://localhost:5009/encoding/utf8
curl http://localhost:5009/encoding/shift-jis

# Media - Test OpenGraph
curl -s http://localhost:5010/ | grep "og:title"

# Anti-Bot - Test rate limiting
for i in {1..10}; do curl http://localhost:5011/; done

# Jobs - Extract Schema.org
curl http://localhost:5012/job/1 | grep -o '"@type":"JobPosting"'

# WebSocket - Test streaming
wscat -c ws://localhost:5013/ws/crawl
```

### Automated Testing

```python
# Example test script
import requests
import json

def test_happy_path():
    """Test basic HTML crawling"""
    response = requests.get("http://localhost:5001/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_jobs_schema():
    """Test Schema.org JobPosting extraction"""
    response = requests.get("http://localhost:5012/api/jobs")
    jobs = response.json()
    assert len(jobs) > 0
    assert jobs[0]["@type"] == "JobPosting"

def test_websocket_streaming():
    """Test WebSocket NDJSON streaming"""
    import websocket
    ws = websocket.create_connection("ws://localhost:5013/ws/crawl")
    ws.send('{"action": "start", "pages": 10}')
    data = ws.recv()
    assert "page" in json.loads(data)
    ws.close()
```

## 📁 Repository Structure

```
riptide-test-sites/
├── README.md                    # This file
├── README.md.OLD                # Previous version (backup)
├── docker-compose.yml           # All 13 sites orchestrated
├── .env.example                 # Environment template
├── MISSION_COMPLETE.txt         # Project completion report
├── FINAL_SUMMARY.md             # Complete project overview
│
├── sites/                       # Site implementations
│   ├── happy-path.site/
│   │   ├── app/
│   │   │   ├── main.py         # FastAPI app
│   │   │   ├── models.py       # Data models
│   │   │   └── data_generator.py
│   │   ├── templates/          # Jinja2 templates
│   │   ├── static/             # CSS, JS, images
│   │   ├── Dockerfile
│   │   └── requirements.txt
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
│
├── docs/                        # Documentation
│   ├── QUICK_REFERENCE.md       # Quick start guide
│   ├── PHASE3_COMPLETION_REPORT.md
│   ├── architecture.md
│   ├── deployment-guide.md
│   ├── development.md
│   └── testing.md
│
└── scripts/                     # Utilities
    ├── health_check.sh
    └── validate_all.sh
```

## 🚢 Deployment Options

### Option 1: Local Development (Default)
**Cost:** Free
**Setup Time:** 5 minutes

```bash
docker-compose up -d
# Access at http://localhost:5001-5013
```

### Option 2: Docker Swarm / Kubernetes
**Cost:** Variable
**Setup Time:** 1-2 hours

Deploy all sites as microservices with:
- Load balancing
- Auto-scaling
- Service discovery
- Health monitoring

### Option 3: Cloud Platforms
**Cost:** Variable (often free tier eligible)
**Setup Time:** 30-60 minutes

Options include:
- Google Cloud Run (free tier available)
- AWS ECS/Fargate
- Azure Container Instances
- DigitalOcean App Platform
- Heroku Container Registry

### Option 4: VPS with Docker Compose
**Cost:** $5-10/month
**Setup Time:** 30 minutes

Deploy to:
- Hetzner Cloud VPS
- DigitalOcean Droplet
- Linode
- Vultr

## 🔧 Configuration

### Environment Variables

Each site supports these variables (via `.env` or docker-compose):

```bash
FAKER_SEED=42          # Faker seed (DO NOT CHANGE for reproducibility)
SITE_NAME=happy-path   # Site identifier
PORT=8000              # Internal container port
DATA_SIZE=100          # Number of entities to generate
DEBUG=true             # Enable debug mode
```

### Customization

**Modify data size:**
```yaml
# docker-compose.yml
environment:
  - DATA_SIZE=200  # Generate 200 items instead of 100
```

**Change ports:**
```yaml
ports:
  - "8001:8000"  # Map to port 8001 instead of 5001
```

**Add custom site:**
```yaml
custom-site:
  build: ./sites/custom-site
  ports:
    - "5014:8000"
  environment:
    - SITE_NAME=custom-site
    - FAKER_SEED=42
```

## 🐛 Troubleshooting

### Sites won't start

```bash
# Check Docker daemon
docker info

# View detailed logs
docker-compose logs happy-path

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Port conflicts

```bash
# Check what's using ports
lsof -i :5001-5013

# Change ports in docker-compose.yml
ports:
  - "6001:8000"  # Use 6001 instead of 5001
```

### Health check failures

```bash
# Wait longer for startup
sleep 15 && docker-compose ps

# Check individual site
curl -v http://localhost:5001/health

# Check container logs
docker-compose logs --tail=100 happy-path
```

### Memory/CPU issues

```bash
# Check resource usage
docker stats --no-stream

# Limit resources per container
services:
  happy-path:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### WebSocket connection issues

```bash
# Test WebSocket directly
wscat -c ws://localhost:5013/ws/crawl

# Check for proxy/firewall blocking
curl -v http://localhost:5013/health

# Enable WebSocket debugging
environment:
  - DEBUG=true
  - WS_DEBUG=true
```

## 📚 Documentation

- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Fast reference guide
- **[FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md)** - Complete project overview
- **[PHASE3_COMPLETION_REPORT.md](docs/PHASE3_COMPLETION_REPORT.md)** - Phase 3 details
- **[architecture.md](docs/architecture.md)** - System design and technical decisions
- **[deployment-guide.md](docs/deployment-guide.md)** - Hosting options and setup
- **[testing.md](docs/testing.md)** - Test strategy and validation

## 🎯 Use Cases

### Web Crawler Development
Test your crawler against:
- Simple HTML pages (happy-path)
- Redirect chains (redirects-canonical)
- Robots.txt compliance (robots-and-sitemaps)
- Rate limiting (slowpoke-and-retries, anti-bot-lite)

### Data Extraction Testing
Validate extraction methods:
- CSS selectors vs LLM (selectors-vs-llm)
- Schema.org metadata (jobs-and-offers)
- Messy HTML parsing (jobs-and-offers: 70% messy)
- OpenGraph/Twitter Cards (media-and-nonhtml)

### Edge Case Validation
Test handling of:
- Character encodings (encoding-and-i18n)
- Binary files (pdfs-and-binaries)
- Authentication flows (auth-and-session)
- JavaScript rendering (static-vs-headless)
- WebSocket streaming (websocket-stream-sink)

### Performance Benchmarking
Measure performance across:
- Simple vs complex pages
- Static vs JavaScript-rendered content
- Synchronous vs WebSocket streaming
- Different content types and encodings

## 🤝 Contributing

### Adding a New Site

1. **Create site directory:**
```bash
mkdir -p sites/new-site.site/app
cd sites/new-site.site
```

2. **Create FastAPI app:**
```python
# app/main.py
from fastapi import FastAPI
from faker import Faker

app = FastAPI()
fake = Faker()
Faker.seed(42)  # ALWAYS use seed 42

@app.get("/")
async def index():
    return {"message": "New site"}

@app.get("/health")
async def health():
    return {"status": "healthy", "site": "new-site"}
```

3. **Update docker-compose.yml:**
```yaml
new-site:
  build: ./sites/new-site.site
  ports:
    - "5014:8000"
  environment:
    - SITE_NAME=new-site
    - FAKER_SEED=42
```

4. **Test the site:**
```bash
docker-compose up -d new-site
curl http://localhost:5014/health
```

### Guidelines
- Always seed Faker with 42 for reproducibility
- Keep sites self-contained (no external dependencies)
- Document site purpose and features
- Include health check endpoint
- Add type hints and docstrings
- Follow FastAPI best practices

## 🔐 Security Notes

- All sites run in isolated Docker containers
- No external database dependencies
- In-memory data generation (stateless)
- No sensitive data (all Faker-generated)
- Suitable for CI/CD environments
- No authentication required (test sites only)
- Auth site uses test credentials only

## 📊 Performance

- **Startup Time:** ~10-15 seconds for all 13 sites
- **Memory:** ~50-100MB per container (~1GB total)
- **CPU:** Minimal (FastAPI is efficient)
- **Storage:** ~200MB total (15MB per site)
- **Network:** Bridge network (minimal overhead)

## 🎊 Project Status

✅ **All 13 sites delivered and operational**

See [MISSION_COMPLETE.txt](MISSION_COMPLETE.txt) for full project completion report.

## 📝 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Faker](https://faker.readthedocs.io/) - Fake data generation
- [Docker](https://www.docker.com/) - Containerization
- [Jinja2](https://jinja.palletsprojects.com/) - Templating engine

## 📞 Support

- **Documentation:** See `/docs` directory
- **Issues:** [GitHub Issues](https://github.com/your-org/riptide-test-sites/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-org/riptide-test-sites/discussions)

---

**Made with ❤️ for reliable web crawling and data extraction testing**
