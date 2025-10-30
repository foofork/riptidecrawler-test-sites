# Test Sites Architecture

## System Overview

A containerized multi-site testing platform consisting of 13 independent web applications, each with deterministic data generation for automated testing and validation.

## Architecture Principles

1. **Isolation**: Each site runs in its own Docker container
2. **Determinism**: All data generation uses Faker with seed=42 for reproducibility
3. **Consistency**: All sites follow the same FastAPI + Jinja2 template pattern
4. **Scalability**: Docker Compose orchestration allows easy scaling and deployment
5. **Testability**: Ground-truth JSON files enable automated validation

## System Components

### 1. Docker Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                         (bridge mode)                        │
├─────────────────────────────────────────────────────────────┤
│  Site 1    Site 2    Site 3    ...    Site 12    Site 13    │
│  :5001     :5002     :5003            :5012      :5013       │
│ [FastAPI] [FastAPI] [FastAPI]  ...  [FastAPI]   [FastAPI]   │
└─────────────────────────────────────────────────────────────┘
```

**Port Mapping**: 5001-5013 (host) → 8000 (container)

### 2. Site Template Architecture

Each site follows this structure:

```
sites/<site-name>/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── data_generator.py   # Faker-based data generation
│   └── routes.py            # API endpoints
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   └── <feature>.html       # Feature-specific pages
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── ground-truth/
│   └── data.json            # Expected test data
├── Dockerfile
├── requirements.txt
└── .env                     # Site-specific config
```

### 3. Data Generation Pattern

All sites use Faker with consistent seeding:

```python
from faker import Faker
fake = Faker()
Faker.seed(42)  # Ensures deterministic data across runs

# Example data generation
users = [
    {
        "id": i,
        "name": fake.name(),
        "email": fake.email(),
        "created": fake.date_time_this_year().isoformat()
    }
    for i in range(100)
]
```

### 4. Ground-Truth Generation Workflow

```
┌──────────────┐
│  Site Launch │
│   (Docker)   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Data Generator   │
│  (Faker seed=42) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  FastAPI Routes  │
│  Render Pages    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Ground-Truth API │
│ /api/ground-truth│
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Export JSON     │
│ ground-truth/    │
│    data.json     │
└──────────────────┘
```

## Site Specifications

### Site Types & Features

1. **E-commerce Site** (Port 5001)
   - Products catalog (100 items)
   - Shopping cart
   - User accounts (50 users)
   - Order history

2. **Blog Platform** (Port 5002)
   - Blog posts (200 posts)
   - Comments (500 comments)
   - Authors (20 authors)
   - Categories & tags

3. **Social Network** (Port 5003)
   - User profiles (100 users)
   - Posts/updates (300 posts)
   - Connections/friends
   - Activity feed

4. **Job Board** (Port 5004)
   - Job listings (150 jobs)
   - Companies (50 companies)
   - Applications
   - Candidate profiles

5. **Real Estate Listings** (Port 5005)
   - Properties (200 listings)
   - Agents (30 agents)
   - Search filters
   - Property details

6. **Restaurant Directory** (Port 5006)
   - Restaurants (100 venues)
   - Menus
   - Reviews (400 reviews)
   - Reservations

7. **Event Management** (Port 5007)
   - Events (80 events)
   - Venues (40 venues)
   - Tickets/registrations
   - Event calendar

8. **Educational Platform** (Port 5008)
   - Courses (60 courses)
   - Students (200 students)
   - Instructors (30 instructors)
   - Enrollments

9. **Healthcare Portal** (Port 5009)
   - Doctors (50 doctors)
   - Appointments (300 appointments)
   - Patients (150 patients)
   - Medical records

10. **Travel Booking** (Port 5010)
    - Destinations (100 destinations)
    - Hotels (200 hotels)
    - Flights
    - Bookings

11. **News Portal** (Port 5011)
    - Articles (300 articles)
    - Journalists (40 journalists)
    - Categories
    - Breaking news

12. **Forum/Community** (Port 5012)
    - Threads (250 threads)
    - Posts (1000 posts)
    - Users (100 users)
    - Categories

13. **Project Management** (Port 5013)
    - Projects (50 projects)
    - Tasks (400 tasks)
    - Team members (60 users)
    - Milestones

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Python**: 3.11+
- **Data Generation**: Faker 20.0+
- **Templating**: Jinja2
- **ASGI Server**: Uvicorn

### Frontend
- **Templates**: Jinja2 HTML
- **CSS**: Custom + Bootstrap 5 (optional)
- **JavaScript**: Vanilla JS for interactivity

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Networking**: Bridge network (isolated)

## Configuration Management

### Environment Variables

Each site requires:
- `SITE_NAME`: Unique identifier
- `FAKER_SEED`: Always 42 for consistency
- `PORT`: Internal port (8000)
- `DATA_SIZE`: Number of entities to generate
- `DEBUG`: Development mode flag

### Docker Compose Configuration

```yaml
version: '3.8'
services:
  site-1:
    build: ./sites/ecommerce
    ports:
      - "5001:8000"
    environment:
      - SITE_NAME=ecommerce
      - FAKER_SEED=42
    networks:
      - test-sites-network
```

## API Endpoints

### Standard Endpoints (All Sites)

- `GET /` - Homepage
- `GET /api/data` - Paginated data
- `GET /api/ground-truth` - Complete ground-truth dataset
- `GET /api/health` - Health check
- `GET /api/stats` - Site statistics

### Site-Specific Endpoints

Each site implements domain-specific endpoints:
- E-commerce: `/products`, `/cart`, `/orders`
- Blog: `/posts`, `/authors`, `/comments`
- Social: `/profiles`, `/posts`, `/connections`
- etc.

## Testing Strategy

### Ground-Truth Validation

1. Launch site via Docker Compose
2. Access `/api/ground-truth` endpoint
3. Compare response with `ground-truth/data.json`
4. Validate data consistency (seed=42 ensures reproducibility)

### Automated Test Flow

```python
# Pseudo-code for automated testing
def test_site(site_url, ground_truth_path):
    response = requests.get(f"{site_url}/api/ground-truth")
    expected = json.load(open(ground_truth_path))
    assert response.json() == expected
```

## Deployment Instructions

### Quick Start

```bash
# Clone repository
git clone <repo-url>
cd riptide-test-sites

# Copy environment template
cp .env.example .env

# Launch all sites
docker-compose up -d

# Verify all sites are running
docker-compose ps

# Access sites
# Site 1: http://localhost:5001
# Site 2: http://localhost:5002
# ... etc
```

### Individual Site Launch

```bash
# Launch specific site
docker-compose up site-1

# View logs
docker-compose logs -f site-1

# Stop site
docker-compose stop site-1
```

## Development Workflow

### Adding a New Site

1. Copy template: `cp -r sites/template sites/new-site`
2. Update `docker-compose.yml` with new service
3. Customize `app/main.py` with site-specific logic
4. Generate ground-truth: Run site and export `/api/ground-truth`
5. Create tests in `tests/test_new_site.py`

### Modifying Existing Site

1. Update code in `sites/<site-name>/app/`
2. Rebuild container: `docker-compose build site-name`
3. Restart service: `docker-compose restart site-name`
4. Regenerate ground-truth if data changes

## Performance Considerations

- **Startup Time**: ~2-3 seconds per site
- **Memory**: ~50MB per container
- **CPU**: Minimal (FastAPI is efficient)
- **Storage**: ~10MB per site (code + data)

## Security Notes

- All sites run in isolated containers
- No external database dependencies
- In-memory data generation (stateless)
- No sensitive data (all generated via Faker)
- Suitable for CI/CD environments

## Monitoring & Logging

### Health Checks

Each site exposes `/api/health`:
```json
{
  "status": "healthy",
  "site": "ecommerce",
  "uptime": 3600,
  "data_generated": true
}
```

### Logging Strategy

- Container logs via `docker-compose logs`
- Structured logging with FastAPI
- Log levels: INFO, WARNING, ERROR

## Complete Infrastructure

### Make Commands Available

All development operations are available via Makefile:

```bash
make up              # Start all 13 sites
make down            # Stop all containers
make build           # Build all images
make restart         # Restart all sites
make logs            # View logs
make health-check    # Verify all sites
make test            # Run test suite
make ground-truth    # Regenerate golden files
make clean           # Remove containers/volumes
make urls            # Display all URLs
```

### Environment Configuration

Complete environment configuration in `.env.example`:
- All 13 sites pre-configured
- Port mappings (5001-5013)
- Data size controls
- Debug settings
- Health check parameters

### Documentation Suite

Comprehensive documentation in `/docs`:
- **architecture.md** - This file (system design)
- **deployment-guide.md** - Hosting options (Hetzner, Cloud Run, Koyeb)
- **development.md** - Contributing guide
- **testing.md** - Test strategy and validation

## Future Enhancements

1. **Database Integration**: Add optional PostgreSQL for persistent data
2. **Authentication**: Implement JWT-based auth across sites
3. **API Gateway**: Centralized routing and rate limiting
4. **Monitoring Dashboard**: Grafana + Prometheus integration
5. **Load Testing**: Artillery/Locust configuration
6. **CI/CD Pipeline**: GitHub Actions for automated testing

## Architecture Decision Records (ADRs)

### ADR-001: FastAPI vs Django
**Decision**: FastAPI
**Rationale**:
- Faster performance
- Built-in API documentation
- Async support
- Lighter weight for test sites

### ADR-002: In-Memory vs Database
**Decision**: In-Memory with Faker
**Rationale**:
- Deterministic testing (seed=42)
- No database management overhead
- Faster container startup
- Stateless design

### ADR-003: Jinja2 Templating
**Decision**: Server-side rendering with Jinja2
**Rationale**:
- Simple integration with FastAPI
- No frontend build complexity
- Sufficient for test site requirements

### ADR-004: Docker Compose vs Kubernetes
**Decision**: Docker Compose
**Rationale**:
- Simpler local development
- Adequate for 13 sites
- Easier debugging
- Lower resource requirements

## Conclusion

This architecture provides a scalable, maintainable, and testable framework for generating 13 diverse web applications with deterministic data. The modular design allows for easy expansion and modification while maintaining consistency across all sites.
