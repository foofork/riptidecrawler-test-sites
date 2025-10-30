# Ground Truth Data Generation Plan

## Overview

This document outlines the plan for generating ground truth validation files for the 10 sites currently missing them. Ground truth files enable automated validation of web crawling and data extraction functionality.

## Missing Ground Truth Sites

The following 10 sites need ground truth files generated:

1. **slowpoke-and-retries.site** (Port 5004)
2. **selectors-vs-llm.site** (Port 5005)
3. **static-vs-headless.site** (Port 5006)
4. **auth-and-session.site** (Port 5008)
5. **pdfs-and-binaries.site** (Port 5007)
6. **encoding-and-i18n.site** (Port 5009)
7. **media-and-nonhtml.site** (Port 5010)
8. **anti-bot-lite.site** (Port 5011)
9. **jobs-and-offers.site** (Port 5012)
10. **websocket-stream-sink** (Port 5013)

## Ground Truth File Format

Based on analysis of existing ground truth files for `happy-path`, `redirects-canonical`, and `robots-and-sitemaps`, each site requires three files:

### 1. `<site-name>.pages.jsonl`

JSONL format (one JSON object per line) containing page crawl data:

```json
{
  "url": "http://localhost:5001/",
  "requested_url": "http://localhost:5001/",
  "depth": 0,
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 10330,
  "canonical_url": null,
  "links_count": 20
}
```

**Fields:**
- `url` (string): Final URL after redirects
- `requested_url` (string): Original requested URL
- `depth` (integer): Depth from root (0 = homepage)
- `status_code` (integer): HTTP response code
- `content_type` (string): MIME type from Content-Type header
- `content_length` (integer): Size of response body in bytes
- `canonical_url` (string|null): Canonical URL from `<link rel="canonical">` tag
- `links_count` (integer): Number of `<a>` tags with href attributes

### 2. `<site-name>.entities.jsonl`

JSONL format containing extracted structured data entities:

```json
{
  "type": "Event",
  "url": "https://happy-path.site/event/1",
  "name": "Sharable bifurcated algorithm",
  "description": "Development say quality throughout beautiful...",
  "startDate": "2025-11-01T00:00:00",
  "endDate": "2025-11-01T03:00:00",
  "location": {
    "@type": "Place",
    "name": "Carter, Fuller and Mcclure",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "310 Kendra Common Apt. 164",
      "addressLocality": "Reidstad",
      "addressRegion": "GA",
      "postalCode": "49021",
      "addressCountry": "US"
    }
  },
  "organizer": {
    "@type": "Organization",
    "name": "Clark-Adams",
    "url": "https://happy-path.site/organizer/1"
  },
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode"
}
```

**Fields:**
- `type` (string): Schema.org entity type (Event, JobPosting, etc.)
- `url` (string): URL where entity was extracted
- `...` (various): All other fields from JSON-LD structured data (excluding `@context` and `@type`)

**Source:** Extracted from `<script type="application/ld+json">` tags in HTML

### 3. `<site-name>.stats.json`

JSON format containing crawl statistics:

```json
{
  "pages_crawled": 110,
  "pages_failed": 0,
  "domains": 1,
  "stop_reason": "max_pages",
  "extraction_methods": {}
}
```

**Fields:**
- `pages_crawled` (integer): Total successful page crawls (status 200)
- `pages_failed` (integer): Total failed page crawls (non-200 status)
- `domains` (integer): Number of unique domains crawled
- `stop_reason` (string): Why crawl stopped ("max_pages", "completed", etc.)
- `extraction_methods` (object): Extraction methods used (currently empty)

## Site-Specific Configurations

Each site has unique characteristics that affect ground truth generation:

### Phase 2 Sites

#### 1. slowpoke-and-retries.site (Port 5004)
- **Purpose:** Resilience testing with artificial delays
- **Expected Pages:** ~20-30
- **Expected Entities:** ~10-20 (Event type)
- **Special Handling:**
  - Longer timeouts (30s+ per request)
  - Retry logic for failed requests
  - Rate limiting detection
- **Entity Type:** Event

#### 2. selectors-vs-llm.site (Port 5005)
- **Purpose:** Compare CSS selector vs LLM extraction
- **Expected Pages:** ~10
- **Expected Entities:** ~10 (Event type)
- **Special Handling:**
  - Extract data using both CSS selectors and from structured data
  - Include extraction method comparison in stats
- **Entity Type:** Event

#### 3. static-vs-headless.site (Port 5006)
- **Purpose:** Detect JavaScript-rendered content
- **Expected Pages:** ~20
- **Expected Entities:** ~15 (Event type)
- **Special Handling:**
  - May require headless browser for JS-rendered pages
  - Document which pages need JS execution
  - Standard crawler should work for static pages
- **Entity Type:** Event

#### 4. pdfs-and-binaries.site (Port 5007)
- **Purpose:** Binary file handling
- **Expected Pages:** ~15 (HTML pages only)
- **Expected Entities:** ~5 (Document type)
- **Special Handling:**
  - Only crawl HTML pages, record binary URLs
  - Track content types: application/pdf, image/*
  - No entity extraction from PDFs (just page records)
- **Entity Type:** Document (if any)

#### 5. auth-and-session.site (Port 5008)
- **Purpose:** Authentication and session management
- **Expected Pages:** ~25
- **Expected Entities:** ~10 (User/Profile type)
- **Special Handling:**
  - Need to authenticate first (POST /login)
  - Session cookies required for protected pages
  - Test credentials: username="testuser", password="testpass"
  - Some pages should return 401/403 without auth
- **Entity Type:** User or Profile

### Phase 3 Sites

#### 6. encoding-and-i18n.site (Port 5009)
- **Purpose:** Character encoding and internationalization
- **Expected Pages:** ~30
- **Expected Entities:** ~20 (Article type)
- **Special Handling:**
  - Multiple character encodings (UTF-8, ISO-8859-1, Shift-JIS, etc.)
  - Detect and handle encoding from Content-Type header
  - RTL text support
  - 10+ different encodings, 20+ languages
- **Entity Type:** Article

#### 7. media-and-nonhtml.site (Port 5010)
- **Purpose:** Multiple content types (JSON, XML, CSV, OpenGraph)
- **Expected Pages:** ~25
- **Expected Entities:** ~15 (Article type)
- **Special Handling:**
  - Multiple content types: text/html, application/json, text/xml, text/csv
  - OpenGraph and Twitter Card metadata extraction
  - May need separate parsers for each content type
- **Entity Type:** Article or Product

#### 8. anti-bot-lite.site (Port 5011)
- **Purpose:** Bot detection and rate limiting
- **Expected Pages:** ~20
- **Expected Entities:** ~10 (Event type)
- **Special Handling:**
  - User-Agent validation (must look like real browser)
  - Rate limiting (max 2 requests/second)
  - Some requests may return 429 (Too Many Requests)
  - Include proper User-Agent header
- **Entity Type:** Event

#### 9. jobs-and-offers.site (Port 5012)
- **Purpose:** JobPosting Schema.org metadata
- **Expected Pages:** ~60
- **Expected Entities:** ~50 (JobPosting type)
- **Special Handling:**
  - 70% messy HTML, 30% clean HTML
  - Focus on JSON-LD extraction (reliable)
  - JobPosting schema with salary, location, etc.
- **Entity Type:** JobPosting

#### 10. websocket-stream-sink (Port 5013)
- **Purpose:** WebSocket streaming and real-time data
- **Expected Pages:** ~10-15 (HTTP pages only)
- **Expected Entities:** ~10 (Event type)
- **Special Handling:**
  - WebSocket endpoint: `ws://localhost:5013/ws/crawl`
  - For ground truth, focus on HTTP endpoints only
  - WebSocket streaming is advanced feature, not required for basic validation
  - Record HTML pages accessible via HTTP
- **Entity Type:** Event

## Generation Strategy

### Step 1: Update Configuration

Add all 10 sites to `SITES_CONFIG` in generation script with proper configurations:

```python
SITES_CONFIG = {
    # ... existing Phase 1 sites ...

    # Phase 2 Sites
    "slowpoke-and-retries": {
        "port": 5004,
        "expected_pages": 25,
        "expected_entities": 15,
        "entity_type": "Event",
        "timeout": 30,
        "retry_attempts": 3
    },
    "selectors-vs-llm": {
        "port": 5005,
        "expected_pages": 10,
        "expected_entities": 10,
        "entity_type": "Event"
    },
    # ... etc for all 10 sites
}
```

### Step 2: Enhanced Crawler Features

Update `GroundTruthGenerator` class to handle:

1. **Authentication:** Session login for auth-and-session.site
2. **Timeouts:** Configurable timeouts for slowpoke-and-retries
3. **Rate Limiting:** Respect rate limits for anti-bot-lite
4. **Content Types:** Handle non-HTML content types
5. **Encoding Detection:** Proper encoding handling for i18n site
6. **User-Agent:** Realistic User-Agent strings

### Step 3: Batch Generation Script

Create `scripts/generate_ground_truth_batch.py` that:

1. Accepts site name as parameter
2. Loads site-specific configuration
3. Performs specialized crawl based on site type
4. Generates all 3 files (.pages.jsonl, .entities.jsonl, .stats.json)
5. Validates output against expected counts
6. Saves to `ground-truth/` directory

### Step 4: Execution Plan

1. **Start all sites:** `docker-compose up -d`
2. **Wait for health checks:** Ensure all sites are ready
3. **Generate ground truth sequentially:** Process one site at a time to avoid resource conflicts
4. **Validate output:** Check file formats and expected counts
5. **Commit to repository:** Add ground truth files to version control

## Validation Criteria

Each ground truth file set must meet these criteria:

### Pages File (`.pages.jsonl`)
- ✅ Valid JSONL format (one JSON object per line)
- ✅ All required fields present
- ✅ Status codes are valid HTTP codes
- ✅ Content types match expected MIME types
- ✅ URLs use localhost base URL
- ✅ Page count within ±5% of expected

### Entities File (`.entities.jsonl`)
- ✅ Valid JSONL format
- ✅ All entities have correct `type` field
- ✅ URLs match pages where entities were found
- ✅ Required Schema.org fields present
- ✅ Entity count within ±5% of expected

### Stats File (`.stats.json`)
- ✅ Valid JSON format
- ✅ All required fields present
- ✅ `pages_crawled` matches successful page count
- ✅ `stop_reason` is valid
- ✅ Totals add up correctly

## Expected Output

After completion, `ground-truth/` directory should contain:

```
ground-truth/
├── happy-path.pages.jsonl          (exists)
├── happy-path.entities.jsonl       (exists)
├── happy-path.stats.json           (exists)
├── redirects-canonical.pages.jsonl (exists)
├── redirects-canonical.entities.jsonl (exists)
├── redirects-canonical.stats.json  (exists)
├── robots-and-sitemaps.pages.jsonl (exists)
├── robots-and-sitemaps.entities.jsonl (exists)
├── robots-and-sitemaps.stats.json  (exists)
├── slowpoke-and-retries.pages.jsonl       (NEW)
├── slowpoke-and-retries.entities.jsonl    (NEW)
├── slowpoke-and-retries.stats.json        (NEW)
├── selectors-vs-llm.pages.jsonl           (NEW)
├── selectors-vs-llm.entities.jsonl        (NEW)
├── selectors-vs-llm.stats.json            (NEW)
├── static-vs-headless.pages.jsonl         (NEW)
├── static-vs-headless.entities.jsonl      (NEW)
├── static-vs-headless.stats.json          (NEW)
├── auth-and-session.pages.jsonl           (NEW)
├── auth-and-session.entities.jsonl        (NEW)
├── auth-and-session.stats.json            (NEW)
├── pdfs-and-binaries.pages.jsonl          (NEW)
├── pdfs-and-binaries.entities.jsonl       (NEW)
├── pdfs-and-binaries.stats.json           (NEW)
├── encoding-and-i18n.pages.jsonl          (NEW)
├── encoding-and-i18n.entities.jsonl       (NEW)
├── encoding-and-i18n.stats.json           (NEW)
├── media-and-nonhtml.pages.jsonl          (NEW)
├── media-and-nonhtml.entities.jsonl       (NEW)
├── media-and-nonhtml.stats.json           (NEW)
├── anti-bot-lite.pages.jsonl              (NEW)
├── anti-bot-lite.entities.jsonl           (NEW)
├── anti-bot-lite.stats.json               (NEW)
├── jobs-and-offers.pages.jsonl            (NEW)
├── jobs-and-offers.entities.jsonl         (NEW)
├── jobs-and-offers.stats.json             (NEW)
├── websocket-stream-sink.pages.jsonl      (NEW)
├── websocket-stream-sink.entities.jsonl   (NEW)
└── websocket-stream-sink.stats.json       (NEW)
```

Total: **39 files** (9 existing + 30 new)

## Execution Commands

### Generate Single Site
```bash
python scripts/generate_ground_truth_batch.py --site slowpoke-and-retries --output ground-truth/
```

### Generate All Missing Sites
```bash
python scripts/generate_ground_truth_batch.py --all-missing --output ground-truth/
```

### Generate All Sites (Including Phase 1)
```bash
python scripts/generate_ground_truth_batch.py --all --output ground-truth/
```

### Validate Generated Files
```bash
python scripts/generate_ground_truth_batch.py --site slowpoke-and-retries --validate
```

## Timeline Estimate

- **Script Enhancement:** 1-2 hours
- **Configuration Setup:** 1 hour
- **Generation + Validation:** 2-3 hours (all 10 sites)
- **Documentation + Testing:** 1 hour
- **Total:** 5-7 hours

## Risk Mitigation

### Potential Issues

1. **Slowpoke timeouts:** Increase timeout to 60s, add retry logic
2. **Auth failures:** Pre-test login credentials, handle 401/403 gracefully
3. **Rate limiting:** Add delays between requests, respect 429 responses
4. **WebSocket complexity:** Skip WebSocket endpoints, focus on HTTP
5. **Binary content:** Don't extract entities from PDFs, just record pages
6. **Encoding errors:** Use chardet for automatic encoding detection

### Fallback Strategy

If automated generation fails for a site:
1. Manual inspection of site structure
2. Hand-craft minimal ground truth set
3. Document limitations in comments
4. Mark as "partial" in validation

## Success Criteria

Ground truth generation is complete when:

- ✅ All 30 files generated (10 sites × 3 files each)
- ✅ All files pass format validation
- ✅ Page counts within expected ranges
- ✅ Entity counts within expected ranges
- ✅ No critical errors during generation
- ✅ Files committed to version control
- ✅ Documentation updated

## Next Steps

1. Create `scripts/generate_ground_truth_batch.py`
2. Test with one site (slowpoke-and-retries)
3. Iterate until working properly
4. Run for all remaining 9 sites
5. Validate all output files
6. Commit to repository
7. Update documentation

## References

- Existing ground truth files: `ground-truth/*.{pages,entities,stats}.{jsonl,json}`
- Current generation script: `scripts/generate_ground_truth.py`
- Site configurations: `sites/*/app/main.py`
- Docker Compose: `docker-compose.yml`
