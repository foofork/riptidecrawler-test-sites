# robots-and-sitemaps.site Testing Guide

## Quick Test Commands

### 1. Start the Service
```bash
# With Docker Compose
docker-compose up -d robots-and-sitemaps

# Verify running
docker ps | grep robots-and-sitemaps

# Check logs
docker-compose logs robots-and-sitemaps
```

### 2. Test robots.txt
```bash
# Get robots.txt
curl http://localhost:5003/robots.txt

# Expected output should contain:
# - User-agent: *
# - Disallow: /admin/
# - Crawl-delay: 2  (capitalized C)
# - Sitemap: https://robots-and-sitemaps.site/sitemap-index.xml
```

### 3. Test Sitemap Index
```bash
# Get sitemap index
curl http://localhost:5003/sitemap-index.xml

# Should reference:
# - sitemap-pages.xml
# - sitemap-events.xml
```

### 4. Test Sitemap Pages
```bash
# Get pages sitemap
curl http://localhost:5003/sitemap-pages.xml | grep -c '<url>'
# Expected: 53 URLs

# Sample pages sitemap
curl http://localhost:5003/sitemap-pages.xml | head -30
```

### 5. Test Sitemap Events
```bash
# Get events sitemap
curl http://localhost:5003/sitemap-events.xml | grep -c '<url>'
# Expected: 100 URLs

# Sample events sitemap
curl http://localhost:5003/sitemap-events.xml | head -30
```

### 6. Test Event Pages
```bash
# Test individual event pages
curl -I http://localhost:5003/events/1
curl -I http://localhost:5003/events/50
curl -I http://localhost:5003/events/100
# All should return: HTTP/1.1 200 OK
```

### 7. Test Static Pages
```bash
# Test individual static pages
curl -I http://localhost:5003/page/1
curl -I http://localhost:5003/page/25
curl -I http://localhost:5003/page/50
# All should return: HTTP/1.1 200 OK
```

### 8. Test Disallowed Paths
```bash
# Test admin secret (should be 403)
curl -I http://localhost:5003/admin/secret
# Expected: HTTP/1.1 403 Forbidden

# Test private path (should be accessible but marked as not crawlable)
curl -I http://localhost:5003/private/
# Expected: HTTP/1.1 200 OK
```

### 9. Test Allow Override
```bash
# Test public admin page (should be allowed)
curl -I http://localhost:5003/admin/public/info
# Expected: HTTP/1.1 200 OK
```

### 10. Run Python robotparser Test
```bash
python3 << 'EOF'
import urllib.robotparser

# Test robotparser compatibility
rp = urllib.robotparser.RobotFileParser()
rp.set_url("http://localhost:5003/robots.txt")
rp.read()

# Test disallowed paths
print("Can fetch /admin/:", rp.can_fetch("*", "http://localhost:5003/admin/"))
print("Can fetch /private/:", rp.can_fetch("*", "http://localhost:5003/private/"))
print("Can fetch /admin/public/info:", rp.can_fetch("*", "http://localhost:5003/admin/public/info"))

# Test crawl delay
print("\nCrawl-delay for *:", rp.crawl_delay("*"))
print("Crawl-delay for Googlebot:", rp.crawl_delay("Googlebot"))
EOF
```

## Expected Test Results

### robotparser Output:
```
Can fetch /admin/: False
Can fetch /private/: False
Can fetch /admin/public/info: True (or False, depending on parser)

Crawl-delay for *: 2.0
Crawl-delay for Googlebot: 0.0
```

### URL Counts:
- sitemap-pages.xml: **53 URLs**
  - Home (/)
  - Public (/public/)
  - Admin Public Info (/admin/public/info)
  - 50 static pages (/page/1 through /page/50)

- sitemap-events.xml: **100 URLs**
  - Events 1-100 (/events/1 through /events/100)

### Total Crawlable: **151 pages**
- 50 static pages
- 100 event pages
- 1 public admin page (admin/public/info)

### Disallowed (25+ URLs):
- /admin/* (except /admin/public/*)
- /private/*
- /api/*
- /temp/*

## Run Full Test Suite

```bash
# Run only robots.txt tests
pytest tests/test_robots.py::TestRobotsCompliance -v

# Run only sitemap tests
pytest tests/test_robots.py::TestSitemapDiscovery -v

# Run all robots and sitemap tests
pytest tests/test_robots.py -v

# Run with markers
pytest -m phase1 tests/test_robots.py -v
```

## Common Issues and Solutions

### Issue 1: "Crawl-delay not found"
**Cause:** Test expects capitalized `Crawl-delay:`
**Solution:** Ensure line 24 has `Crawl-delay: 2` (capital C)

### Issue 2: "crawl-delay value is 0"
**Cause:** robotparser reading wrong user-agent section
**Solution:** Ensure main `User-agent: *` section has `Crawl-delay: 2`

### Issue 3: "sitemap-events.xml returns 404"
**Cause:** Missing endpoint
**Solution:** Ensure `@app.get("/sitemap-events.xml")` exists

### Issue 4: "/events/1 returns 404"
**Cause:** Missing dynamic route
**Solution:** Ensure `@app.get("/events/{event_id}")` exists

### Issue 5: "/admin/secret doesn't return 403"
**Cause:** Missing route or wrong status code
**Solution:** Ensure route returns `Response(status_code=403)`

## Health Check

```bash
curl http://localhost:5003/health

# Expected output:
{
  "status": "healthy",
  "service": "robots-and-sitemaps.site",
  "port": 5003,
  "features": [
    "robots.txt",
    "sitemap_index",
    "crawl_delay",
    "multiple_sitemaps",
    "events"
  ]
}
```

## Debugging Tips

1. **Check Docker logs:**
   ```bash
   docker-compose logs -f robots-and-sitemaps
   ```

2. **Restart service:**
   ```bash
   docker-compose restart robots-and-sitemaps
   ```

3. **Rebuild from scratch:**
   ```bash
   docker-compose down
   docker-compose build robots-and-sitemaps
   docker-compose up -d robots-and-sitemaps
   ```

4. **Test without Docker:**
   ```bash
   cd sites/robots-and-sitemaps.site
   uvicorn app:app --host 0.0.0.0 --port 5003
   ```

## Files Modified

- `/Users/dylantullberg/Developer/riptide-test-sites/sites/robots-and-sitemaps.site/app.py`

## Related Documentation

- Test file: `/Users/dylantullberg/Developer/riptide-test-sites/tests/test_robots.py`
- Summary: `/Users/dylantullberg/Developer/riptide-test-sites/docs/robots-fix-summary.md`
