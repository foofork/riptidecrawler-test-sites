# Integration Guide: Using RipTide Test Sites with Your Crawler

**For developers who want to test their web crawlers against comprehensive, reproducible test scenarios**

---

## 🎯 Overview

This guide shows you how to integrate RipTide Test Sites into your crawler project for testing. Whether you're building a Rust crawler, Python scraper, Node.js spider, or any other web extraction tool, these test sites provide 13 comprehensive scenarios to validate your implementation.

---

## 🚀 Quick Start (3 Options)

### Option 1: Local Development with Shared Docker Network

**Best for:** Day-to-day development, debugging, quick iteration

**Setup:**

```bash
# Terminal 1: Start test sites (in this repo)
cd riptide-test-sites
docker-compose up -d

# Terminal 2: Run your crawler tests (in your repo)
cd ../your-crawler-project
export TEST_SITES_BASE_URL=http://localhost
npm test  # or cargo test, pytest, etc.
```

**Pros:** Simple, fast, easy to debug
**Cons:** Requires manual startup, port conflicts possible

---

### Option 2: GitHub Actions CI/CD Integration

**Best for:** Continuous integration, automated testing, PR validation

**Add to your `.github/workflows/test.yml`:**

```yaml
name: Crawler Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout your crawler
        uses: actions/checkout@v4
        with:
          path: crawler

      - name: Checkout test sites
        uses: actions/checkout@v4
        with:
          repository: foofork/riptidecrawler-test-sites
          path: test-sites

      - name: Start test sites
        working-directory: test-sites
        run: |
          docker-compose up -d
          echo "Waiting for services to be healthy..."
          timeout 90 bash -c 'until curl -f http://localhost:5001/health; do sleep 3; done'

      - name: Verify all sites are running
        run: |
          for port in {5001..5013}; do
            curl -f http://localhost:$port/health || exit 1
          done

      - name: Run crawler tests
        working-directory: crawler
        env:
          TEST_SITES_BASE_URL: http://localhost
        run: |
          # Your test command here
          npm test                # Node.js
          # cargo test            # Rust
          # pytest tests/         # Python
          # mvn test              # Java

      - name: Cleanup
        if: always()
        working-directory: test-sites
        run: docker-compose down -v
```

**Pros:** Automated, consistent, great for CI/CD
**Cons:** Slower feedback loop than local dev

---

### Option 3: Git Submodule (Optional)

**Best for:** Teams that want test sites versioned with their crawler

```bash
# In your crawler repo
git submodule add https://github.com/foofork/riptidecrawler-test-sites tests/fixtures
git submodule update --init --recursive

# Start test sites
cd tests/fixtures
docker-compose up -d
```

**Update submodule to latest:**
```bash
cd tests/fixtures
git pull origin main
cd ../..
git add tests/fixtures
git commit -m "Update test sites to latest version"
```

**Pros:** Version-locked, team consistency
**Cons:** Extra Git complexity, submodule management

---

## 🧪 Integration Examples by Language/Framework

### Rust (RipTideCrawler, Scrapy-rs, etc.)

**`tests/integration_test.rs`:**

```rust
use std::env;

const TEST_SITES: &[(u16, &str)] = &[
    (5001, "happy-path"),
    (5002, "redirects-canonical"),
    (5003, "robots-and-sitemaps"),
    (5004, "slowpoke-and-retries"),
    (5005, "selectors-vs-llm"),
    (5006, "static-vs-headless"),
    (5007, "pdfs-and-binaries"),
    (5008, "auth-and-session"),
    (5009, "encoding-and-i18n"),
    (5010, "media-and-nonhtml"),
    (5011, "anti-bot-lite"),
    (5012, "jobs-and-offers"),
    (5013, "websocket-stream-sink"),
];

fn get_base_url() -> String {
    env::var("TEST_SITES_BASE_URL")
        .unwrap_or_else(|_| "http://localhost".to_string())
}

#[tokio::test]
async fn test_happy_path_basic_crawl() {
    let base_url = get_base_url();
    let url = format!("{}:5001", base_url);

    let result = your_crawler::crawl(&url).await.unwrap();

    assert!(result.success);
    assert!(result.pages_crawled > 0);
    assert_eq!(result.errors.len(), 0);
}

#[tokio::test]
async fn test_redirect_handling() {
    let base_url = get_base_url();
    let url = format!("{}:5002/redirect-chain/3", base_url);

    let result = your_crawler::crawl(&url).await.unwrap();

    assert!(result.followed_redirects);
    assert_eq!(result.final_url, format!("{}:5002/final-destination", base_url));
}

#[tokio::test]
async fn test_robots_txt_compliance() {
    let base_url = get_base_url();
    let url = format!("{}:5003", base_url);

    let result = your_crawler::crawl(&url).await.unwrap();

    assert!(result.respected_robots_txt);
    assert!(!result.crawled_pages.contains("/private/"));
}

#[tokio::test]
async fn test_js_rendering() {
    let base_url = get_base_url();
    let url = format!("{}:5006/js-rendered", base_url);

    let result = your_crawler::crawl(&url).await.unwrap();

    // Should detect JS-rendered content
    assert!(result.required_headless);
    assert!(result.content.contains("JavaScript rendered this"));
}

#[tokio::test]
async fn test_all_sites_health() {
    let base_url = get_base_url();

    for (port, name) in TEST_SITES.iter() {
        let health_url = format!("{}:{}/health", base_url, port);
        let resp = reqwest::get(&health_url).await.unwrap();

        assert_eq!(resp.status(), 200, "Site {} is not healthy", name);

        let json: serde_json::Value = resp.json().await.unwrap();
        assert_eq!(json["status"], "healthy");
    }
}
```

---

### Python (Scrapy, BeautifulSoup, Playwright, etc.)

**`tests/test_integration.py`:**

```python
import os
import pytest
import requests
from your_crawler import Crawler

BASE_URL = os.getenv("TEST_SITES_BASE_URL", "http://localhost")

TEST_SITES = [
    (5001, "happy-path"),
    (5002, "redirects-canonical"),
    (5003, "robots-and-sitemaps"),
    (5004, "slowpoke-and-retries"),
    (5005, "selectors-vs-llm"),
    (5006, "static-vs-headless"),
    (5007, "pdfs-and-binaries"),
    (5008, "auth-and-session"),
    (5009, "encoding-and-i18n"),
    (5010, "media-and-nonhtml"),
    (5011, "anti-bot-lite"),
    (5012, "jobs-and-offers"),
    (5013, "websocket-stream-sink"),
]

@pytest.fixture
def crawler():
    return Crawler(base_url=BASE_URL)

def test_happy_path_basic_crawl(crawler):
    """Test basic HTML crawling and extraction"""
    result = crawler.crawl(f"{BASE_URL}:5001")

    assert result.success
    assert result.pages_crawled > 0
    assert len(result.errors) == 0

def test_redirect_handling(crawler):
    """Test redirect chain following"""
    result = crawler.crawl(f"{BASE_URL}:5002/redirect-chain/3")

    assert result.followed_redirects
    assert result.final_url == f"{BASE_URL}:5002/final-destination"

def test_robots_txt_compliance(crawler):
    """Test robots.txt parsing and compliance"""
    result = crawler.crawl(f"{BASE_URL}:5003")

    assert result.respected_robots_txt
    assert not any("/private/" in url for url in result.crawled_urls)

def test_sitemap_parsing(crawler):
    """Test XML sitemap parsing"""
    sitemap = crawler.parse_sitemap(f"{BASE_URL}:5003/sitemap.xml")

    assert len(sitemap.urls) > 0
    assert all(url.startswith(f"{BASE_URL}:5003") for url in sitemap.urls)

def test_session_authentication(crawler):
    """Test login and session management"""
    result = crawler.crawl(
        f"{BASE_URL}:5008",
        auth={"username": "testuser", "password": "testpass123"}
    )

    assert result.authenticated
    assert result.session_maintained

def test_pdf_extraction(crawler):
    """Test PDF download and text extraction"""
    result = crawler.crawl(f"{BASE_URL}:5007/documents/sample.pdf")

    assert result.content_type == "application/pdf"
    assert result.extracted_text is not None
    assert len(result.extracted_text) > 0

@pytest.mark.parametrize("port,name", TEST_SITES)
def test_all_sites_health(port, name):
    """Verify all test sites are healthy"""
    response = requests.get(f"{BASE_URL}:{port}/health", timeout=10)

    assert response.status_code == 200, f"Site {name} is not healthy"

    data = response.json()
    assert data["status"] == "healthy"
    assert data["site"] == name

def test_websocket_streaming(crawler):
    """Test WebSocket real-time streaming"""
    import websocket

    ws = websocket.create_connection(f"ws://localhost:5013/ws/crawl")
    ws.send('{"action":"start","pages":5}')

    results = []
    for _ in range(5):
        result = ws.recv()
        results.append(result)

    ws.close()

    assert len(results) == 5
```

---

### Node.js (Puppeteer, Cheerio, Axios, etc.)

**`tests/integration.test.js`:**

```javascript
const axios = require('axios');
const { Crawler } = require('../src/crawler');

const BASE_URL = process.env.TEST_SITES_BASE_URL || 'http://localhost';

const TEST_SITES = [
  { port: 5001, name: 'happy-path' },
  { port: 5002, name: 'redirects-canonical' },
  { port: 5003, name: 'robots-and-sitemaps' },
  { port: 5004, name: 'slowpoke-and-retries' },
  { port: 5005, name: 'selectors-vs-llm' },
  { port: 5006, name: 'static-vs-headless' },
  { port: 5007, name: 'pdfs-and-binaries' },
  { port: 5008, name: 'auth-and-session' },
  { port: 5009, name: 'encoding-and-i18n' },
  { port: 5010, name: 'media-and-nonhtml' },
  { port: 5011, name: 'anti-bot-lite' },
  { port: 5012, name: 'jobs-and-offers' },
  { port: 5013, name: 'websocket-stream-sink' },
];

describe('RipTide Test Sites Integration', () => {
  let crawler;

  beforeAll(() => {
    crawler = new Crawler({ baseUrl: BASE_URL });
  });

  test('happy path - basic crawl', async () => {
    const result = await crawler.crawl(`${BASE_URL}:5001`);

    expect(result.success).toBe(true);
    expect(result.pagesCrawled).toBeGreaterThan(0);
    expect(result.errors).toHaveLength(0);
  });

  test('redirect handling', async () => {
    const result = await crawler.crawl(`${BASE_URL}:5002/redirect-chain/3`);

    expect(result.followedRedirects).toBe(true);
    expect(result.finalUrl).toBe(`${BASE_URL}:5002/final-destination`);
  });

  test('robots.txt compliance', async () => {
    const result = await crawler.crawl(`${BASE_URL}:5003`);

    expect(result.respectedRobotsTxt).toBe(true);
    expect(result.crawledUrls.some(url => url.includes('/private/'))).toBe(false);
  });

  test('JavaScript rendering detection', async () => {
    const result = await crawler.crawl(`${BASE_URL}:5006/js-rendered`);

    expect(result.requiredHeadless).toBe(true);
    expect(result.content).toContain('JavaScript rendered this');
  });

  test('Schema.org JSON-LD parsing', async () => {
    const result = await crawler.crawl(`${BASE_URL}:5012/api/jobs`);
    const jobs = JSON.parse(result.content);

    expect(jobs).toHaveLength(50);
    expect(jobs[0]['@type']).toBe('JobPosting');
    expect(jobs[0]).toHaveProperty('title');
    expect(jobs[0]).toHaveProperty('description');
  });

  test.each(TEST_SITES)('$name site health check', async ({ port, name }) => {
    const response = await axios.get(`${BASE_URL}:${port}/health`);

    expect(response.status).toBe(200);
    expect(response.data.status).toBe('healthy');
    expect(response.data.site).toBe(name);
  });

  test('WebSocket streaming', async () => {
    const WebSocket = require('ws');
    const ws = new WebSocket(`ws://localhost:5013/ws/crawl`);

    return new Promise((resolve, reject) => {
      const results = [];

      ws.on('open', () => {
        ws.send(JSON.stringify({ action: 'start', pages: 5 }));
      });

      ws.on('message', (data) => {
        results.push(JSON.parse(data));

        if (results.length === 5) {
          ws.close();
          expect(results).toHaveLength(5);
          resolve();
        }
      });

      ws.on('error', reject);
    });
  });
});
```

---

## 🔧 Configuration Best Practices

### Environment Variables

**Create `.env.test` in your crawler repo:**

```bash
# Test Sites Configuration
TEST_SITES_BASE_URL=http://localhost
TEST_SITES_TIMEOUT=30

# Individual site ports (if needed)
HAPPY_PATH_PORT=5001
REDIRECTS_PORT=5002
ROBOTS_PORT=5003
SLOWPOKE_PORT=5004
SELECTORS_PORT=5005
STATIC_PORT=5006
PDFS_PORT=5007
AUTH_PORT=5008
ENCODING_PORT=5009
MEDIA_PORT=5010
ANTIBOT_PORT=5011
JOBS_PORT=5012
WEBSOCKET_PORT=5013
```

### Test Configuration Files

**`pytest.ini` (Python):**

```ini
[pytest]
testpaths = tests
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow (deselect with '-m "not slow"')
env =
    TEST_SITES_BASE_URL=http://localhost
```

**`Cargo.toml` (Rust):**

```toml
[[test]]
name = "integration"
path = "tests/integration_test.rs"
harness = true

[dev-dependencies]
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
serde_json = "1"
```

**`package.json` (Node.js):**

```json
{
  "scripts": {
    "test": "jest",
    "test:integration": "TEST_SITES_BASE_URL=http://localhost jest --testPathPattern=integration"
  },
  "jest": {
    "testEnvironment": "node",
    "testTimeout": 30000,
    "setupFilesAfterEnv": ["./tests/setup.js"]
  }
}
```

---

## 📊 Test Coverage Checklist

Use this checklist to ensure your crawler handles all scenarios:

### Basic Functionality
- [ ] **Happy Path** (5001): Basic HTML crawling and extraction
- [ ] **Pagination**: Follow paginated content
- [ ] **Links**: Extract and follow internal links

### URL Handling
- [ ] **Redirects** (5002): Follow 301/302 redirect chains
- [ ] **Canonical URLs**: Respect `<link rel="canonical">`
- [ ] **URL Normalization**: Handle query params, fragments

### Standards Compliance
- [ ] **robots.txt** (5003): Parse and respect robots.txt
- [ ] **Sitemaps** (5003): Parse XML sitemaps
- [ ] **Rate Limiting** (5004): Respect rate limits

### Resilience
- [ ] **Retries** (5004): Retry failed requests
- [ ] **Timeouts** (5004): Handle slow responses
- [ ] **Error Handling**: Graceful degradation

### Extraction Methods
- [ ] **CSS Selectors** (5005): Extract with CSS/XPath
- [ ] **LLM Fallback** (5005): Intelligent extraction
- [ ] **Schema.org** (5012): Parse JSON-LD structured data

### Rendering
- [ ] **Static HTML** (5006): Fast static parsing
- [ ] **JavaScript** (5006): Headless browser fallback
- [ ] **Routing Logic**: Choose appropriate rendering method

### Content Types
- [ ] **HTML**: Standard web pages
- [ ] **JSON** (5010): API responses
- [ ] **XML** (5010): RSS/Atom feeds
- [ ] **PDF** (5007): Document extraction
- [ ] **Images** (5007): Binary downloads
- [ ] **CSV** (5010): Structured data

### Authentication
- [ ] **Login Forms** (5008): Form-based auth
- [ ] **Session Management** (5008): Cookie handling
- [ ] **Protected Content**: Access gated content

### Internationalization
- [ ] **UTF-8** (5009): Unicode handling
- [ ] **Other Encodings** (5009): ISO-8859-1, Windows-1252
- [ ] **RTL Languages** (5009): Arabic, Hebrew
- [ ] **Multilingual** (5009): Language detection

### Edge Cases
- [ ] **Bot Detection** (5011): User-Agent handling
- [ ] **CAPTCHA** (5011): Detection and handling
- [ ] **Messy HTML** (5012): Malformed markup
- [ ] **Real-time** (5013): WebSocket streaming

---

## 🐛 Troubleshooting

### Issue: "Connection refused" errors

**Cause:** Test sites not running or wrong port

**Fix:**
```bash
# Check if sites are running
docker-compose ps

# Verify health endpoints
curl http://localhost:5001/health

# Restart if needed
docker-compose restart
```

### Issue: Tests timing out

**Cause:** Sites still starting up

**Fix:**
```bash
# Add proper health check wait in CI
timeout 90 bash -c 'until curl -f http://localhost:5001/health; do sleep 3; done'

# Or in code (Python example)
import time
import requests

def wait_for_sites(timeout=90):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get("http://localhost:5001/health")
            if r.ok:
                return True
        except:
            pass
        time.sleep(3)
    raise TimeoutError("Test sites did not start in time")
```

### Issue: Port conflicts (5001-5013 already in use)

**Fix:** Change ports in docker-compose.yml
```yaml
happy-path:
  ports:
    - "6001:8000"  # Change external port
```

Then update your tests:
```bash
export HAPPY_PATH_PORT=6001
```

### Issue: WebSocket tests failing

**Cause:** Proxy or firewall blocking WebSocket connections

**Fix:**
```bash
# Test WebSocket directly
wscat -c ws://localhost:5013/ws/crawl

# Check for proxy environment variables
unset http_proxy https_proxy
```

---

## 🎯 Performance Tips

### 1. Run Only Needed Sites

```bash
# Start just one site for focused testing
docker-compose up -d happy-path

# Or specific sites
docker-compose up -d happy-path redirects-canonical robots-and-sitemaps
```

### 2. Parallel Testing

```yaml
# GitHub Actions matrix strategy
strategy:
  matrix:
    test-suite:
      - basic      # Sites 5001-5003
      - advanced   # Sites 5004-5007
      - expert     # Sites 5008-5013

steps:
  - name: Start relevant sites
    run: |
      if [[ "${{ matrix.test-suite }}" == "basic" ]]; then
        docker-compose up -d happy-path redirects-canonical robots-and-sitemaps
      fi
```

### 3. Cache Docker Images

```yaml
# GitHub Actions caching
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
```

---

## 📝 Example Project Structure

```
your-crawler-project/
├── .github/
│   └── workflows/
│       └── test.yml              # CI with test sites
├── src/
│   ├── crawler.rs                # Your crawler code
│   └── ...
├── tests/
│   ├── integration_test.rs       # Integration tests
│   ├── fixtures/                 # Git submodule (optional)
│   │   └── riptide-test-sites/
│   └── ...
├── scripts/
│   ├── start-test-sites.sh       # Helper script
│   └── wait-for-sites.sh         # Health check waiter
├── .env.test                      # Test configuration
├── Cargo.toml / package.json     # Dependencies
└── README.md                      # Document test setup
```

---

## 🚢 Production Readiness Validation

Before deploying your crawler, verify it passes all test sites:

```bash
# Full integration test suite
./scripts/start-test-sites.sh
npm test                           # Run all tests
./scripts/stop-test-sites.sh

# Generate coverage report
npm run test:coverage

# Validate against ground truth
cd riptide-test-sites
python scripts/generate_ground_truth.py --all --validate
```

**Success Criteria:**
- ✅ All 13 sites pass health checks
- ✅ 100% of core scenarios pass
- ✅ 90%+ of edge cases handled
- ✅ No unhandled exceptions
- ✅ Respects robots.txt and rate limits

---

## 🤝 Contributing Test Scenarios

Found a crawler edge case not covered? Contribute to the test sites!

1. Fork `riptidecrawler-test-sites` repo
2. Add new test scenario in `sites/`
3. Update `docker-compose.yml`
4. Add tests and documentation
5. Submit a PR

See [Contributing Guide](https://github.com/foofork/riptidecrawler-test-sites#contributing) for details.

---

## 📚 Additional Resources

- **Test Sites Repository**: https://github.com/foofork/riptidecrawler-test-sites
- **Quick Reference**: [docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Architecture**: [docs/architecture.md](architecture.md)
- **Ground Truth Data**: [docs/GROUND_TRUTH_QUICK_REFERENCE.md](GROUND_TRUTH_QUICK_REFERENCE.md)

---

## 💡 Tips for Success

1. **Start Simple**: Begin with happy-path (5001) before tackling advanced scenarios
2. **Use Health Checks**: Always verify sites are ready before testing
3. **Run Incrementally**: Test one site at a time during development
4. **Check Ground Truth**: Use provided ground truth data to validate extraction
5. **Monitor Resources**: These are lightweight, but 13 containers add up
6. **Version Lock**: Pin test sites version in CI for reproducibility
7. **Document Setup**: Add integration instructions to your project's README

---

**Questions or Issues?**

- Open an issue: https://github.com/foofork/riptidecrawler-test-sites/issues
- Check examples: See real implementations in RipTideCrawler repo

**Happy Crawling! 🕷️**
