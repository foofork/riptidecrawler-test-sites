# Phase 2: Complex Test Sites

Advanced scraping scenarios with authentication, rate limiting, binary files, and intelligent routing.

## Overview

Phase 2 contains 5 complex test sites that simulate real-world scraping challenges:

1. **selectors-vs-llm.site** (Port 5002) - CSS selector reliability testing
2. **static-vs-headless.site** (Port 5003) - Static vs JavaScript content detection
3. **slowpoke-and-retries.site** (Port 5007) - Timeout and retry logic testing
4. **auth-and-session.site** (Port 5008) - Authentication and session management
5. **pdfs-and-binaries.site** (Port 5004) - Binary file handling and Content-Type detection

## 1. selectors-vs-llm.site (Port 5002)

Tests when CSS selectors work vs when LLM extraction is needed.

### Features
- **70% Clean Pages**: Semantic HTML with proper classes and data-testid attributes
- **30% Messy Pages**: Unstructured HTML requiring LLM extraction
- **Confidence Scores**: Each page reports extraction confidence (0-1)
- **Table Variations**: Clean vs messy table structures

### Endpoints
```
GET /                    # Home page with overview
GET /clean/{item_id}     # Clean product page (confidence: 0.95)
GET /messy/{item_id}     # Messy product page (confidence: 0.45)
GET /table-clean         # Well-structured table
GET /table-messy         # Poorly-structured table
GET /metrics             # Extraction metrics and recommendations
```

### Testing Strategy
```python
# Check confidence score to decide extraction method
response = requests.get("http://localhost:5002/clean/0")
soup = BeautifulSoup(response.text, 'html.parser')

# Clean pages - use CSS selectors
if "CLEAN HTML" in response.text:
    title = soup.select_one('[data-testid="product-name"]').text
    price = soup.select_one('[data-testid="product-price"]').text

# Messy pages - use LLM extraction
else:
    # Extract with LLM or more complex logic
    pass
```

### Key Files
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/selectors-vs-llm.site/app.py`
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/selectors-vs-llm.site/templates/*.html`

---

## 2. static-vs-headless.site (Port 5003)

Tests intelligent routing between static parsing and headless browser execution.

### Features
- **75% Static Pages**: Content available in initial HTML
- **25% Dynamic Pages**: JavaScript-required content (fetch on load)
- **Bot Detection**: navigator.webdriver detection page
- **Routing Logic**: Recommendations for parser selection

### Endpoints
```
GET /                        # Home page
GET /static/{article_id}     # Static HTML article
GET /dynamic/{article_id}    # JavaScript-required article
GET /api/article/{id}        # API for dynamic content
GET /anti-bot-check          # Test navigator.webdriver detection
GET /api/bot-check           # Bot detection results
GET /routing-logic           # Routing recommendations JSON
```

### Testing Strategy
```python
# Check data-requires-js attribute
response = requests.get("http://localhost:5003/static/0")
soup = BeautifulSoup(response.text, 'html.parser')

if soup.body.get('data-requires-js') == 'true':
    # Use headless browser (Playwright/Selenium)
    pass
else:
    # Use static parser (BeautifulSoup/lxml)
    pass
```

### Anti-Bot Detection
The `/anti-bot-check` endpoint detects:
- `navigator.webdriver === true` (Selenium/Playwright detection)
- "headless" in user agent string

Use stealth mode or undetected-chromedriver to bypass.

### Key Files
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/static-vs-headless.site/app.py`
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/static-vs-headless.site/templates/*.html`

---

## 3. slowpoke-and-retries.site (Port 5007)

Tests timeout handling, rate limiting, and exponential backoff (inspired by httpbin.org).

### Features
- **Configurable Delays**: /delay/{seconds} endpoint
- **Rate Limiting**: 5 requests per 60 seconds with Retry-After headers
- **Unstable Endpoint**: Randomly returns 200, 429, or 503
- **Timeout Test**: 60-second hang endpoint
- **Custom Status Codes**: Return any HTTP status for testing

### Endpoints
```
GET /delay/{seconds}         # Delay response by N seconds
GET /rate-limited            # Rate limited endpoint (5/min)
GET /unstable                # Random 200/429/503 responses
GET /timeout                 # Hangs for 60 seconds
GET /503-error               # Always returns 503
GET /retry-test?attempt=N    # Succeeds on 3rd attempt
GET /status/{code}           # Return any HTTP status code
```

### Testing Strategy
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry logic
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1,
    respect_retry_after_header=True
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)

# Test rate limiting
for i in range(10):
    response = session.get("http://localhost:5007/rate-limited")
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited! Retry after {retry_after}s")
```

### Headers to Check
- `Retry-After`: Seconds to wait before retry
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Unix timestamp of window reset

### Key Files
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/slowpoke-and-retries.site/app.py`
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/slowpoke-and-retries.site/templates/home.html`

---

## 4. auth-and-session.site (Port 5008)

Tests authentication flows, session management, and CSRF protection.

### Features
- **Login Form**: Username/password authentication
- **Session Cookies**: HttpOnly cookies with 1-hour expiration
- **CSRF Protection**: Token-based CSRF protection
- **Protected Endpoints**: Require authentication
- **Session Persistence**: Session info and logout

### Endpoints
```
GET /                    # Login page (or redirect to dashboard)
POST /login              # Handle login (requires CSRF token)
GET /dashboard           # Protected dashboard page
GET /protected-data      # Protected API endpoint
POST /logout             # Logout and destroy session
GET /session-info        # Current session information
```

### Test Credentials
```
Username: admin
Password: password123

Username: user
Password: test123
```

### Testing Strategy
```python
import requests

session = requests.Session()

# 1. Get login page and CSRF token
response = session.get("http://localhost:5008/")
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

# 2. Login with credentials
login_data = {
    'username': 'admin',
    'password': 'password123',
    'csrf_token': csrf_token
}
response = session.post("http://localhost:5008/login", data=login_data)

# 3. Access protected endpoint
protected = session.get("http://localhost:5008/protected-data")
print(protected.json())  # Success!

# 4. Get CSRF token for logout
dashboard = session.get("http://localhost:5008/dashboard")
soup = BeautifulSoup(dashboard.text, 'html.parser')
logout_csrf = soup.find('input', {'name': 'csrf_token'})['value']

# 5. Logout
session.post("http://localhost:5008/logout", data={'csrf_token': logout_csrf})
```

### Session Details
- **Cookie Name**: `session_id`
- **Duration**: 1 hour
- **Attributes**: HttpOnly, SameSite=Lax
- **Storage**: In-memory (use Redis in production)

### Key Files
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/auth-and-session.site/app.py`
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/auth-and-session.site/templates/*.html`

---

## 5. pdfs-and-binaries.site (Port 5004)

Tests binary file detection, PDF generation, and Content-Type handling.

### Features
- **PDF Generation**: Using ReportLab with tables
- **Image Files**: PNG images
- **Video Files**: MP4 videos
- **Binary Files**: Generic binary data
- **Mixed Content**: HTML pages with binary links
- **Content-Type Detection**: Proper MIME types

### Endpoints
```
GET /                    # Home page with file overview
GET /pdf/simple          # Simple PDF without tables
GET /pdf/with-table      # PDF with data table
GET /image/{image_id}    # PNG image
GET /video/{video_id}    # MP4 video
GET /binary/{file_id}    # Generic binary file
GET /mixed-content       # HTML page with binary links
GET /content-types       # Content-Type map JSON
```

### Testing Strategy
```python
import requests

# Check Content-Type before parsing
response = requests.get("http://localhost:5004/pdf/simple")
content_type = response.headers.get('Content-Type')

if content_type.startswith('text/html'):
    # Parse as HTML
    soup = BeautifulSoup(response.content, 'html.parser')
elif content_type == 'application/pdf':
    # Extract PDF content
    import PyPDF2
    # Skip or use PDF parser
    pass
elif content_type.startswith('image/'):
    # Handle image
    pass
else:
    # Skip other binary types
    print(f"Skipping {content_type}")
```

### Content-Type Map
```json
{
  "html_pages": [
    {"url": "/", "content_type": "text/html"},
    {"url": "/mixed-content", "content_type": "text/html"}
  ],
  "pdfs": [
    {"url": "/pdf/simple", "content_type": "application/pdf"},
    {"url": "/pdf/with-table", "content_type": "application/pdf"}
  ],
  "images": [
    {"url": "/image/1", "content_type": "image/png"}
  ],
  "videos": [
    {"url": "/video/1", "content_type": "video/mp4"}
  ],
  "binaries": [
    {"url": "/binary/1", "content_type": "application/octet-stream"}
  ]
}
```

### PDF Extraction
PDFs contain:
- Title paragraphs
- Body text (Faker-generated)
- Data tables (5 rows, 3 columns)

Use PyPDF2 or pdfplumber to extract content.

### Key Files
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/pdfs-and-binaries.site/app.py`
- `/Users/dylantullberg/Developer/riptide-test-sites/sites/pdfs-and-binaries.site/templates/*.html`

---

## Running Phase 2 Sites

### Individual Sites

```bash
# Site 1: Selectors vs LLM (Port 5002)
cd sites/selectors-vs-llm.site
pip install -r requirements.txt
python app.py

# Site 2: Static vs Headless (Port 5003)
cd sites/static-vs-headless.site
pip install -r requirements.txt
python app.py

# Site 3: Slowpoke and Retries (Port 5007)
cd sites/slowpoke-and-retries.site
pip install -r requirements.txt
python app.py

# Site 4: Auth and Session (Port 5008)
cd sites/auth-and-session.site
pip install -r requirements.txt
python app.py

# Site 5: PDFs and Binaries (Port 5004)
cd sites/pdfs-and-binaries.site
pip install -r requirements.txt
python app.py
```

### Docker Deployment

```bash
# Build all Phase 2 sites
docker build -t selectors-vs-llm sites/selectors-vs-llm.site
docker build -t static-vs-headless sites/static-vs-headless.site
docker build -t slowpoke-retries sites/slowpoke-and-retries.site
docker build -t auth-session sites/auth-and-session.site
docker build -t pdfs-binaries sites/pdfs-and-binaries.site

# Run all sites
docker run -d -p 5002:5002 --name selectors selectors-vs-llm
docker run -d -p 5003:5003 --name static static-vs-headless
docker run -d -p 5007:5007 --name slowpoke slowpoke-retries
docker run -d -p 5008:5008 --name auth auth-session
docker run -d -p 5004:5004 --name pdfs pdfs-binaries
```

### Docker Compose (Recommended)

Create `docker-compose.phase2.yml`:

```yaml
version: '3.8'

services:
  selectors-vs-llm:
    build: ./sites/selectors-vs-llm.site
    ports:
      - "5002:5002"
    restart: unless-stopped

  static-vs-headless:
    build: ./sites/static-vs-headless.site
    ports:
      - "5003:5003"
    restart: unless-stopped

  slowpoke-and-retries:
    build: ./sites/slowpoke-and-retries.site
    ports:
      - "5007:5007"
    restart: unless-stopped

  auth-and-session:
    build: ./sites/auth-and-session.site
    ports:
      - "5008:5008"
    restart: unless-stopped

  pdfs-and-binaries:
    build: ./sites/pdfs-and-binaries.site
    ports:
      - "5004:5004"
    restart: unless-stopped
```

Run:
```bash
docker-compose -f docker-compose.phase2.yml up -d
```

---

## Testing Scenarios

### 1. Extraction Method Selection
Test when to use CSS selectors vs LLM extraction:
```python
# Visit selectors-vs-llm.site
confidence = get_confidence_score(url)
if confidence > 0.7:
    use_css_selectors()
else:
    use_llm_extraction()
```

### 2. Intelligent Routing
Route to appropriate parser based on JavaScript requirements:
```python
# Visit static-vs-headless.site
if requires_javascript(url):
    use_headless_browser()
else:
    use_static_parser()
```

### 3. Retry Logic
Implement exponential backoff with Retry-After headers:
```python
# Visit slowpoke-and-retries.site
max_retries = 3
for attempt in range(max_retries):
    response = requests.get(url)
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
    else:
        break
```

### 4. Session Management
Maintain authentication across requests:
```python
# Visit auth-and-session.site
session = requests.Session()
login(session, username, password, csrf_token)
data = session.get("/protected-data").json()
```

### 5. Content-Type Detection
Skip non-HTML content appropriately:
```python
# Visit pdfs-and-binaries.site
response = requests.get(url)
if not response.headers.get('Content-Type').startswith('text/html'):
    skip_or_handle_binary(response)
```

---

## Port Assignments

| Site | Port | Purpose |
|------|------|---------|
| selectors-vs-llm.site | 5002 | CSS vs LLM extraction |
| static-vs-headless.site | 5003 | Static vs JS rendering |
| pdfs-and-binaries.site | 5004 | Binary file handling |
| slowpoke-and-retries.site | 5007 | Timeout and retry logic |
| auth-and-session.site | 5008 | Authentication testing |

---

## Key Learning Objectives

1. **Extraction Confidence**: Learn when CSS selectors are reliable vs when LLM extraction is needed
2. **Intelligent Routing**: Route to static parser or headless browser based on page requirements
3. **Resilience**: Handle rate limits, timeouts, and server errors with proper retry logic
4. **Authentication**: Manage sessions, cookies, and CSRF tokens in scraping workflows
5. **Content Detection**: Detect and handle different content types (HTML, PDF, images, videos)

---

## Next Steps

After testing Phase 2 sites:
1. Implement confidence-based extraction method selection
2. Add intelligent routing logic to your scraper
3. Configure retry strategies with exponential backoff
4. Add session management for authenticated scraping
5. Implement Content-Type detection and skip logic

All sites use Faker with seed=42 for reproducible test data.
