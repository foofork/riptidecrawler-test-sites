# RipTide Test Sites

A containerized multi-site testing platform consisting of 13 independent web applications with deterministic data generation for automated testing and validation.

## 🚀 Quick Start (5 Minutes)

```bash
# Clone repository
git clone <repo-url>
cd riptide-test-sites

# Configure environment (optional - defaults work)
cp .env.example .env

# Start all 13 sites
make up

# Verify all sites are running
make health-check

# View all site URLs
make urls
```

**Access Sites:**
- E-commerce: http://localhost:5001
- Blog: http://localhost:5002
- Social Network: http://localhost:5003
- Job Board: http://localhost:5004
- Real Estate: http://localhost:5005
- Restaurant: http://localhost:5006
- Events: http://localhost:5007
- Education: http://localhost:5008
- Healthcare: http://localhost:5009
- Travel: http://localhost:5010
- News: http://localhost:5011
- Forum: http://localhost:5012
- Project Management: http://localhost:5013

## 📋 What This Is

RipTide Test Sites provides **13 deterministic web applications** for testing web crawling, extraction, and validation capabilities. Each site uses **seeded fake data** (Faker with seed=42) to ensure reproducible results across test runs.

### Key Features

✅ **Deterministic Data** - Same data every time (seed=42)
✅ **Isolated Containers** - Each site runs independently
✅ **Ground Truth Validation** - Golden files for automated testing
✅ **Health Monitoring** - Built-in health checks for all sites
✅ **Fast Startup** - All 13 sites start in ~10 seconds
✅ **Zero Dependencies** - No external APIs or databases needed

## 🏗️ Architecture

Each site is a **FastAPI application** running in Docker with:
- JSON-LD structured data (Schema.org)
- Semantic HTML for CSS selectors
- Pagination (10 items per page)
- Health check endpoints
- Ground-truth API for validation

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

| # | Site Name | Port | Purpose | Data Size |
|---|-----------|------|---------|-----------|
| 1 | **E-commerce** | 5001 | Products, cart, orders | 100 products, 50 users |
| 2 | **Blog** | 5002 | Posts, comments, authors | 200 posts, 500 comments |
| 3 | **Social Network** | 5003 | Profiles, posts, connections | 100 users, 300 posts |
| 4 | **Job Board** | 5004 | Jobs, companies, applications | 150 jobs, 50 companies |
| 5 | **Real Estate** | 5005 | Properties, agents, search | 200 listings, 30 agents |
| 6 | **Restaurant** | 5006 | Venues, menus, reviews | 100 restaurants, 400 reviews |
| 7 | **Events** | 5007 | Events, venues, tickets | 80 events, 40 venues |
| 8 | **Education** | 5008 | Courses, students, instructors | 60 courses, 200 students |
| 9 | **Healthcare** | 5009 | Doctors, appointments, patients | 50 doctors, 300 appointments |
| 10 | **Travel** | 5010 | Destinations, hotels, flights | 100 destinations, 200 hotels |
| 11 | **News** | 5011 | Articles, journalists, categories | 300 articles, 40 journalists |
| 12 | **Forum** | 5012 | Threads, posts, users | 250 threads, 1000 posts |
| 13 | **Project Mgmt** | 5013 | Projects, tasks, teams | 50 projects, 400 tasks |

## 🛠️ Development Workflow

### Start/Stop Sites

```bash
# Start all sites
make up

# Start specific site
make up-ecommerce

# Stop all sites
make down

# Restart all sites
make restart

# Restart specific site
make restart-blog
```

### View Logs

```bash
# View all logs (follow mode)
make logs

# View logs for specific site
make logs-social

# View last 50 lines
docker-compose logs --tail=50 ecommerce
```

### Health Checks

```bash
# Check all sites
make health-check

# Check specific site
curl http://localhost:5001/api/health

# Expected response:
# {
#   "status": "healthy",
#   "site": "ecommerce",
#   "uptime": 3600,
#   "data_generated": true
# }
```

### Testing

```bash
# Run full test suite
make test

# Run specific test file
pytest tests/test_ecommerce.py -v

# Validate against ground truth
make validate

# Regenerate ground truth files
make ground-truth
```

### Resource Monitoring

```bash
# Show container status
make ps

# Show resource usage
make stats

# View all URLs
make urls
```

## 🧪 Testing Strategy

### Ground Truth Validation

Each site maintains ground-truth JSON files that capture expected data:

```
ground-truth/
├── ecommerce.pages.jsonl      # Page crawl results
├── ecommerce.stats.json       # Crawl statistics
├── ecommerce.entities.jsonl   # Extracted entities
└── ... (per site)
```

**Validation Workflow:**

1. Start site: `make up-ecommerce`
2. Access ground-truth API: `http://localhost:5001/api/ground-truth`
3. Compare with golden file: `ground-truth/ecommerce.pages.jsonl`
4. Assert data matches (seed=42 ensures reproducibility)

**Automated Testing:**

```python
# tests/test_ecommerce.py
def test_ecommerce_ground_truth():
    response = requests.get("http://localhost:5001/api/ground-truth")
    expected = json.load(open("ground-truth/ecommerce.pages.jsonl"))
    assert response.json() == expected
```

## 📁 Repository Structure

```
riptide-test-sites/
├── README.md                    # This file
├── Makefile                     # Development commands
├── docker-compose.yml           # All 13 sites orchestrated
├── .env.example                 # Environment template
├── Plan.md                      # Detailed implementation plan
├── Roadmap.md                   # Phased rollout plan
├── Deployment.md                # Hosting options guide
│
├── sites/                       # Site implementations
│   ├── ecommerce/
│   │   ├── app/
│   │   │   ├── main.py         # FastAPI app
│   │   │   ├── models.py       # Pydantic models
│   │   │   ├── data_generator.py
│   │   │   └── routes.py
│   │   ├── templates/          # Jinja2 templates
│   │   ├── static/             # CSS, JS, images
│   │   ├── ground-truth/       # Golden files
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env
│   ├── blog/
│   ├── social/
│   └── ... (13 total)
│
├── tests/                       # E2E tests
│   ├── conftest.py
│   ├── test_ecommerce.py
│   ├── test_blog.py
│   └── requirements.txt
│
├── scripts/                     # Utilities
│   ├── generate_ground_truth.py
│   ├── validate_fixtures.py
│   └── health_check.sh
│
└── docs/                        # Documentation
    ├── architecture.md
    ├── deployment-guide.md
    ├── development.md
    └── testing.md
```

## 🚢 Deployment Options

### Option 1: Local Development (Default)
**Cost:** Free
**Setup Time:** 5 minutes

```bash
docker-compose up -d
# Access at http://localhost:5001-5013
```

### Option 2: Hetzner VPS + Coolify (Recommended)
**Cost:** €3.49/month ($4/month) for ALL 13 sites
**Setup Time:** 45 minutes

Deploy all sites with automatic HTTPS and subdomains:
- http://ecommerce.1.2.3.4.sslip.io
- http://blog.1.2.3.4.sslip.io
- ... (all 13 sites)

📖 **Full guide:** See `docs/deployment-guide.md`

### Option 3: Google Cloud Run (Free Tier)
**Cost:** $0-8/month (likely stays FREE)
**Setup Time:** 30 minutes

Auto-generated URLs with HTTPS:
- https://ecommerce-abc123.run.app
- https://blog-xyz789.run.app

### Option 4: GitHub Actions (CI/CD)
**Cost:** Free for public repos

Pre-built Docker images on GitHub Container Registry for fast CI builds.

📖 **Complete deployment guide:** `docs/deployment-guide.md`

## 🔧 Configuration

### Environment Variables

Each site supports these variables (via `.env` or docker-compose):

```bash
FIXTURE_SEED=42          # Faker seed (DO NOT CHANGE for reproducibility)
SITE_NAME=ecommerce      # Site identifier
PORT=8000                # Internal container port
DATA_SIZE=100            # Number of entities to generate
DEBUG=true               # Enable debug mode
```

### Customization

**Modify data size:**
```yaml
# docker-compose.yml
environment:
  - DATA_SIZE=200  # Generate 200 products instead of 100
```

**Change ports:**
```yaml
ports:
  - "8001:8000"  # Map to port 8001 instead of 5001
```

## 🐛 Troubleshooting

### Sites won't start
```bash
# Check Docker daemon
docker info

# View detailed logs
docker-compose logs ecommerce

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
sleep 10 && make health-check

# Check individual site
curl -v http://localhost:5001/api/health

# Verify data generation
curl http://localhost:5001/api/stats
```

### Memory/CPU issues
```bash
# Check resource usage
make stats

# Limit resources per container
services:
  ecommerce:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## 📚 Documentation

- **[Architecture](docs/architecture.md)** - System design and technical decisions
- **[Deployment Guide](docs/deployment-guide.md)** - Hosting options and setup
- **[Development Guide](docs/development.md)** - Contributing and extending
- **[Testing Guide](docs/testing.md)** - Test strategy and validation

## 🤝 Contributing

### Adding a New Site

1. **Copy template:**
```bash
cp -r sites/template sites/new-site
```

2. **Update docker-compose.yml:**
```yaml
new-site:
  build: ./sites/new-site
  ports:
    - "5014:8000"
  environment:
    - SITE_NAME=new-site
    - FIXTURE_SEED=42
```

3. **Implement FastAPI app:**
```python
# sites/new-site/app/main.py
from fastapi import FastAPI
from faker import Faker

app = FastAPI()
fake = Faker()
Faker.seed(42)

@app.get("/")
async def index():
    return {"message": "New site"}
```

4. **Generate ground truth:**
```bash
make ground-truth SITE=new-site
```

5. **Create tests:**
```python
# tests/test_new_site.py
def test_new_site():
    response = requests.get("http://localhost:5014/api/health")
    assert response.status_code == 200
```

### Guidelines
- Always seed Faker with 42 for reproducibility
- Keep sites self-contained (no external dependencies)
- Document site purpose and features
- Include ground-truth validation
- Add health check endpoint

## 🔐 Security Notes

- All sites run in isolated Docker containers
- No external database dependencies
- In-memory data generation (stateless)
- No sensitive data (all Faker-generated)
- Suitable for CI/CD environments
- No authentication required (test sites only)

## 📊 Performance

- **Startup Time:** ~10 seconds for all 13 sites
- **Memory:** ~50MB per container (~650MB total)
- **CPU:** Minimal (FastAPI is efficient)
- **Storage:** ~130MB total (10MB per site)

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

**Made with ❤️ for reliable web testing**
