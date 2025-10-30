# Redirects & Canonical URLs Test Site

FastAPI application for testing HTTP redirects (301/302) and canonical URL handling.

## Features

- **301 Permanent Redirects**: Single and multi-hop chains
- **302 Temporary Redirects**: Single and multi-hop chains
- **Redirect Chains**: Up to 3-hop chains (301→302→final)
- **Canonical URLs**: Original and duplicate pages with proper canonical tags
- **Absolute/Relative**: Tests both URL types

## Running the Site

### Development
```bash
pip install -r requirements.txt
python app.py
```

### Docker
```bash
docker build -t redirects-canonical-site .
docker run -p 5005:5005 redirects-canonical-site
```

Visit: http://localhost:5005

## Endpoints

### 301 Redirects
- `GET /redirect/301/{n}` - N-hop 301 redirect chain
- `GET /absolute-redirect/301/{n}` - Absolute URL 301 redirects

### 302 Redirects
- `GET /redirect/302/{n}` - N-hop 302 redirect chain
- `GET /absolute-redirect/302/{n}` - Absolute URL 302 redirects

### Redirect Chains
- `GET /chain/start` - 3-hop chain: 301→302→final
- `GET /chain/middle` - 302→final
- `GET /chain/final` - Final destination
- `GET /mixed-chain/start` - Alternative mixed chain

### Canonical URLs
- `GET /canonical/original` - Original page (self-canonical)
- `GET /canonical/duplicate1` - Duplicate pointing to original
- `GET /canonical/duplicate2` - Another duplicate pointing to original

### Utility
- `GET /final` - Final redirect destination
- `GET /robots.txt` - Robots file
- `GET /sitemap.xml` - XML sitemap

## Testing

```bash
# Test 301 redirect (should return 301 status)
curl -I http://localhost:5005/redirect/301/1

# Test 3-hop 301 chain
curl -I http://localhost:5005/redirect/301/3

# Test 302 redirect
curl -I http://localhost:5005/redirect/302/1

# Follow redirect chain
curl -L http://localhost:5005/chain/start

# Check canonical tag
curl http://localhost:5005/canonical/duplicate1 | grep canonical

# Test mixed chain
curl -L http://localhost:5005/mixed-chain/start
```

## Redirect Behavior

**301 Permanent Redirect:**
- Search engines consolidate link signals to destination
- Browsers cache the redirect
- Use for permanent URL changes

**302 Temporary Redirect:**
- Search engines keep both URLs in index
- No caching by browsers
- Use for temporary moves

**Canonical URLs:**
- Tells search engines which version is preferred
- Duplicates won't compete in search results
- All duplicates point to original with `<link rel="canonical">`

## robots.txt

Blocks intermediate redirect URLs from crawling:
- `/redirect/*` - Disallowed
- `/chain/start` - Disallowed
- `/canonical/original` - Allowed (canonical)
- Final destinations - Allowed
