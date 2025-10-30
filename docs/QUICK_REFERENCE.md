# Quick Reference: All 13 Test Sites

## 🚀 Quick Start Commands

```bash
# Build and run all sites
cd /Users/dylantullberg/Developer/riptide-test-sites/sites
docker-compose up -d

# Check all health endpoints
for port in 5000 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010 5012 5013; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r .status)"
done
```

## 📋 Site Inventory

| Port | Site Name | Purpose | Key Features |
|------|-----------|---------|--------------|
| 5000 | happy-path.site | Foundation | Clean HTML, simple crawling |
| 5001 | static-vs-headless.site | JS Rendering | Static vs dynamic content |
| 5002 | selectors-vs-llm.site | Extraction | CSS vs LLM comparison |
| 5003 | robots-and-sitemaps.site | Standards | Robots.txt, sitemaps |
| 5004 | redirects-canonical.site | Navigation | Redirects, canonical URLs |
| 5005 | auth-and-session.site | Security | Login, sessions, cookies |
| 5006 | pdfs-and-binaries.site | Files | PDF, images, downloads |
| 5007 | slowpoke-and-retries.site | Resilience | Slow responses, retries |
| 5008 | anti-bot-lite.site | Protection | Basic bot detection |
| 5009 | encoding-and-i18n.site | I18n | Charsets, languages |
| 5010 | media-and-nonhtml.site | Media | Video, audio, metadata |
| 5012 | jobs-and-offers.site | Schema | JobPosting, mixed HTML |
| 5013 | websocket-stream-sink | Streaming | Real-time WebSocket |

## 🎯 Testing URLs

### Phase 1 (Foundation)
```bash
http://localhost:5000          # Happy path
http://localhost:5001          # Static vs headless
http://localhost:5002          # Selectors vs LLM
http://localhost:5003          # Robots & sitemaps
```

### Phase 2 (Intermediate)
```bash
http://localhost:5004          # Redirects & canonical
http://localhost:5005          # Auth & sessions
http://localhost:5006          # PDFs & binaries
http://localhost:5007          # Slow & retries
http://localhost:5008          # Anti-bot
```

### Phase 3 (Advanced)
```bash
http://localhost:5009          # Encoding & i18n
http://localhost:5010          # Media & non-HTML
http://localhost:5012          # Jobs & offers
http://localhost:5013          # WebSocket streaming
```

## 🔍 Testing Scenarios

### CSS Selector Testing
```bash
# Clean HTML (jobs 1-15)
curl http://localhost:5012/job/5
```

### LLM Extraction Testing
```bash
# Messy HTML (jobs 16-50)
curl http://localhost:5012/job/30
```

### WebSocket Testing
```javascript
const ws = new WebSocket('ws://localhost:5013/ws/crawl');
ws.onopen = () => ws.send(JSON.stringify({action: 'crawl', url: 'example.com'}));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

### Schema.org Validation
```bash
# Extract JobPosting JSON-LD
curl http://localhost:5012/job/1 | grep -A 30 'application/ld+json'
```

## 📊 Health Check

```bash
# Check all sites
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
curl http://localhost:5005/health
curl http://localhost:5006/health
curl http://localhost:5007/health
curl http://localhost:5008/health
curl http://localhost:5009/health
curl http://localhost:5010/health
curl http://localhost:5012/health
curl http://localhost:5013/health
```

## 🐳 Docker Commands

```bash
# Build specific site
cd sites/jobs-and-offers.site
docker build -t jobs-site .

# Run specific site
docker run -p 5012:5012 jobs-site

# Stop all sites
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild specific site
docker-compose up -d --build jobs-and-offers-site
```

## 📁 File Locations

```
/Users/dylantullberg/Developer/riptide-test-sites/
├── sites/
│   ├── happy-path.site/
│   ├── static-vs-headless.site/
│   ├── selectors-vs-llm.site/
│   ├── robots-and-sitemaps.site/
│   ├── redirects-canonical.site/
│   ├── auth-and-session.site/
│   ├── pdfs-and-binaries.site/
│   ├── slowpoke-and-retries.site/
│   ├── anti-bot-lite.site/
│   ├── encoding-and-i18n.site/
│   ├── media-and-nonhtml.site/
│   ├── jobs-and-offers.site/
│   └── websocket-stream-sink/
└── docs/
    ├── PHASE3_COMPLETION_REPORT.md
    └── QUICK_REFERENCE.md (this file)
```

## 🎯 Common Test Cases

### 1. Test CSS vs LLM Extraction (jobs-and-offers.site)
```python
# Test clean HTML (CSS selectors work)
import requests
from bs4 import BeautifulSoup

response = requests.get('http://localhost:5012/job/5')
soup = BeautifulSoup(response.text, 'html.parser')
title = soup.select_one('[data-testid="job-title"]').text
# Should work easily

# Test messy HTML (LLM required)
response = requests.get('http://localhost:5012/job/30')
soup = BeautifulSoup(response.text, 'html.parser')
# CSS selectors won't work reliably - need LLM
```

### 2. Test WebSocket Streaming (websocket-stream-sink)
```python
import asyncio
import websockets
import json

async def test_stream():
    async with websockets.connect('ws://localhost:5013/ws/crawl') as ws:
        await ws.send(json.dumps({'action': 'crawl', 'url': 'example.com'}))
        async for msg in ws:
            print(json.loads(msg))

asyncio.run(test_stream())
```

### 3. Test Schema.org Extraction
```python
import json
from bs4 import BeautifulSoup

response = requests.get('http://localhost:5012/job/10')
soup = BeautifulSoup(response.text, 'html.parser')
jsonld = soup.find('script', type='application/ld+json')
job_data = json.loads(jsonld.string)
print(job_data['@type'])  # Should be "JobPosting"
```

## 📚 API Endpoints

### jobs-and-offers.site (5012)
```bash
GET /                    # Homepage with all jobs
GET /job/{id}           # Individual job page
GET /api/jobs           # JSON API - all jobs
GET /api/job/{id}       # JSON API - single job
GET /health             # Health check
```

### websocket-stream-sink (5013)
```bash
GET /                    # Interactive web UI
WS  /ws/crawl           # WebSocket endpoint
GET /health             # Health check
```

## 🔧 Troubleshooting

### Site won't start
```bash
# Check if port is in use
lsof -i :5012

# Kill process on port
kill -9 $(lsof -t -i:5012)

# Check Docker logs
docker-compose logs jobs-and-offers-site
```

### WebSocket connection fails
```bash
# Test WebSocket connectivity
wscat -c ws://localhost:5013/ws/crawl

# Check server logs
docker logs websocket-stream-sink
```

### Health check fails
```bash
# Detailed health check
curl -v http://localhost:5012/health

# Check container status
docker ps | grep jobs-site
```

## 📊 Statistics

- **Total Sites:** 13
- **Total Ports:** 5000-5013 (excluding 5011)
- **Total Files:** 100+ (Python, HTML, config)
- **Total Code:** ~100KB
- **Technologies:** FastAPI, WebSockets, Jinja2, Docker

## 🎉 Quick Win Commands

```bash
# Test everything at once
for port in 5000 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010 5012 5013; do
  curl -s http://localhost:$port/health | jq
done

# Open all sites in browser (macOS)
for port in 5000 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010 5012 5013; do
  open http://localhost:$port
done

# Get all job listings
curl http://localhost:5012/api/jobs | jq '.jobs[] | {title, company, extraction_method}'

# Test WebSocket in browser console
const ws = new WebSocket('ws://localhost:5013/ws/crawl');
ws.onopen = () => ws.send(JSON.stringify({action: 'crawl', url: 'test-site.local'}));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

**Generated:** October 30, 2025
**Status:** All 13 sites operational ✅
