# Ground Truth Generation Quick Reference

## TL;DR - Generate All Missing Ground Truth

```bash
# 1. Start all sites
docker-compose up -d

# 2. Wait for sites to be ready (15 seconds)
sleep 15

# 3. Generate ground truth for all 10 missing sites
python scripts/generate_ground_truth_batch.py --all-missing

# 4. Done! Files saved to ground-truth/
```

## File Format Summary

Each site gets 3 files in `ground-truth/` directory:

| File | Format | Contains |
|------|--------|----------|
| `<site>.pages.jsonl` | JSONL | Page crawl data (URL, status, content type, etc.) |
| `<site>.entities.jsonl` | JSONL | Extracted entities (Events, Jobs, Articles, etc.) |
| `<site>.stats.json` | JSON | Crawl statistics (pages crawled, failed, stop reason) |

## Command Examples

### Generate Single Site
```bash
python scripts/generate_ground_truth_batch.py --site slowpoke-and-retries
```

### Generate All Missing Sites (Phase 2 & 3)
```bash
python scripts/generate_ground_truth_batch.py --all-missing
```

### Generate All Sites (Re-generate Phase 1 too)
```bash
python scripts/generate_ground_truth_batch.py --all
```

### Validate Existing Files (No Generation)
```bash
python scripts/generate_ground_truth_batch.py --site jobs-and-offers --validate-only
```

### Generate Without Validation
```bash
python scripts/generate_ground_truth_batch.py --site anti-bot-lite --skip-validation
```

### Custom Output Directory
```bash
python scripts/generate_ground_truth_batch.py --all-missing --output my-ground-truth/
```

## Sites Needing Ground Truth

| Site Name | Port | Entity Type | Expected Pages | Expected Entities |
|-----------|------|-------------|----------------|-------------------|
| slowpoke-and-retries | 5004 | Event | 25 | 15 |
| selectors-vs-llm | 5005 | Event | 10 | 10 |
| static-vs-headless | 5006 | Event | 20 | 15 |
| pdfs-and-binaries | 5007 | Document | 15 | 5 |
| auth-and-session | 5008 | User | 25 | 10 |
| encoding-and-i18n | 5009 | Article | 30 | 20 |
| media-and-nonhtml | 5010 | Article | 25 | 15 |
| anti-bot-lite | 5011 | Event | 20 | 10 |
| jobs-and-offers | 5012 | JobPosting | 60 | 50 |
| websocket-stream-sink | 5013 | Event | 15 | 10 |

## Special Site Handling

### slowpoke-and-retries
- Longer timeouts (30s)
- Automatic retry logic (3 attempts)
- Rate limiting delays

### auth-and-session
- Automatic authentication with test credentials
- Username: `testuser`, Password: `testpass`
- Handles protected pages

### anti-bot-lite
- Uses realistic User-Agent
- Rate limiting (0.5s between requests)
- Respects 429 (Too Many Requests) responses

### pdfs-and-binaries
- Skips binary file downloads
- Only crawls HTML pages
- Records binary URLs but doesn't download

### encoding-and-i18n
- Automatic encoding detection
- Handles UTF-8, ISO-8859-1, Shift-JIS, etc.
- Respects Content-Type charset declarations

### websocket-stream-sink
- Only crawls HTTP endpoints
- Skips WebSocket connections for ground truth
- Focus on static pages

## Validation Criteria

Each ground truth set is validated against:

- **Page Count:** Within ±10% of expected (minimum ±2 pages)
- **Entity Count:** Within ±10% of expected (minimum ±2 entities)
- **Entity Types:** All entities match expected Schema.org type
- **File Format:** Valid JSONL and JSON formats
- **Required Fields:** All mandatory fields present

## Troubleshooting

### Sites Not Responding
```bash
# Check if sites are running
docker-compose ps

# Check specific site health
curl http://localhost:5004/health
```

### Timeout Errors
```bash
# Increase timeout for slow sites
python scripts/generate_ground_truth_batch.py --site slowpoke-and-retries
# (Script already has 30s timeout for this site)
```

### Authentication Failures
```bash
# Test login manually
curl -X POST http://localhost:5008/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

### Rate Limiting (429 Errors)
```bash
# Script automatically handles rate limiting with delays
# For anti-bot-lite: 0.5s between requests
# For slowpoke-and-retries: 1s between requests
```

### Encoding Issues
```bash
# Script automatically detects encoding from Content-Type header
# For manual testing:
curl -i http://localhost:5009/encoding/utf8
curl -i http://localhost:5009/encoding/shift-jis
```

## Expected Results

After running `--all-missing`, you should see:

```
ground-truth/
├── slowpoke-and-retries.pages.jsonl       (NEW - ~25 pages)
├── slowpoke-and-retries.entities.jsonl    (NEW - ~15 entities)
├── slowpoke-and-retries.stats.json        (NEW)
├── selectors-vs-llm.pages.jsonl           (NEW - ~10 pages)
├── selectors-vs-llm.entities.jsonl        (NEW - ~10 entities)
├── selectors-vs-llm.stats.json            (NEW)
├── static-vs-headless.pages.jsonl         (NEW - ~20 pages)
├── static-vs-headless.entities.jsonl      (NEW - ~15 entities)
├── static-vs-headless.stats.json          (NEW)
├── pdfs-and-binaries.pages.jsonl          (NEW - ~15 pages)
├── pdfs-and-binaries.entities.jsonl       (NEW - ~5 entities)
├── pdfs-and-binaries.stats.json           (NEW)
├── auth-and-session.pages.jsonl           (NEW - ~25 pages)
├── auth-and-session.entities.jsonl        (NEW - ~10 entities)
├── auth-and-session.stats.json            (NEW)
├── encoding-and-i18n.pages.jsonl          (NEW - ~30 pages)
├── encoding-and-i18n.entities.jsonl       (NEW - ~20 entities)
├── encoding-and-i18n.stats.json           (NEW)
├── media-and-nonhtml.pages.jsonl          (NEW - ~25 pages)
├── media-and-nonhtml.entities.jsonl       (NEW - ~15 entities)
├── media-and-nonhtml.stats.json           (NEW)
├── anti-bot-lite.pages.jsonl              (NEW - ~20 pages)
├── anti-bot-lite.entities.jsonl           (NEW - ~10 entities)
├── anti-bot-lite.stats.json               (NEW)
├── jobs-and-offers.pages.jsonl            (NEW - ~60 pages)
├── jobs-and-offers.entities.jsonl         (NEW - ~50 entities)
├── jobs-and-offers.stats.json             (NEW)
├── websocket-stream-sink.pages.jsonl      (NEW - ~15 pages)
├── websocket-stream-sink.entities.jsonl   (NEW - ~10 entities)
└── websocket-stream-sink.stats.json       (NEW)
```

**Total:** 30 new files (10 sites × 3 files each)

## Time Estimates

| Operation | Time |
|-----------|------|
| Single simple site | 10-30 seconds |
| Single complex site | 30-90 seconds |
| All 10 missing sites | 5-10 minutes |
| All 13 sites | 7-15 minutes |

## Next Steps After Generation

1. **Review Files:** Check that files were created correctly
```bash
ls -lh ground-truth/*.{jsonl,json} | tail -30
```

2. **Validate Counts:**
```bash
# Count pages in each file
for f in ground-truth/*.pages.jsonl; do
  echo "$(basename $f): $(wc -l < $f) pages"
done

# Count entities in each file
for f in ground-truth/*.entities.jsonl; do
  echo "$(basename $f): $(wc -l < $f) entities"
done
```

3. **Commit to Repository:**
```bash
git add ground-truth/
git commit -m "Add ground truth data for Phase 2 & 3 sites"
```

4. **Use for Testing:**
```python
# Example: Load and validate against ground truth
import json

# Load pages
with open('ground-truth/jobs-and-offers.pages.jsonl') as f:
    pages = [json.loads(line) for line in f]

# Load entities
with open('ground-truth/jobs-and-offers.entities.jsonl') as f:
    entities = [json.loads(line) for line in f]

# Load stats
with open('ground-truth/jobs-and-offers.stats.json') as f:
    stats = json.load(f)

print(f"Expected {stats['pages_crawled']} pages, got {len(pages)}")
print(f"Expected {len(entities)} JobPosting entities")
```

## Help & Documentation

- **Full Plan:** `docs/GROUND_TRUTH_GENERATION_PLAN.md`
- **Script Help:** `python scripts/generate_ground_truth_batch.py --help`
- **Site Docs:** `README.md`
- **Testing Guide:** `docs/testing.md`
