# Robots.txt & Sitemaps Test Site

FastAPI application for testing complex robots.txt rules and sitemap indexes.

## Features

- **Complex robots.txt**: Multiple user-agent rules with Allow/Disallow directives
- **Crawl-Delay Testing**: Different delays per bot (0-2 seconds)
- **Sitemap Index**: Multi-sitemap architecture with specialized sitemaps
- **50+ URLs**: Blog posts, products, and pages in organized sitemaps
- **User-Agent Specific Rules**: Different rules for Googlebot, Bingbot, etc.

## Running the Site

### Development
```bash
pip install -r requirements.txt
python app.py
```

### Docker
```bash
docker build -t robots-sitemaps-site .
docker run -p 5006:5006 robots-sitemaps-site
```

Visit: http://localhost:5006

## Endpoints

### Robots & Sitemaps
- `GET /robots.txt` - Complex robots.txt with multiple user-agents
- `GET /sitemap-index.xml` - Sitemap index pointing to 3 sitemaps
- `GET /sitemap-main.xml` - Main pages sitemap (4 URLs)
- `GET /sitemap-blog.xml` - Blog posts sitemap (20 URLs)
- `GET /sitemap-products.xml` - Products sitemap (30 URLs)

### Allowed Pages
- `GET /` - Homepage
- `GET /public/` - Public page
- `GET /blog/` - Blog index
- `GET /blog/post-{id}` - Blog posts (1-20)
- `GET /products/item-{id}` - Products (1-30)
- `GET /about` - About page
- `GET /contact` - Contact page

### Blocked Pages
- `GET /private/` - Private area (Disallowed)
- `GET /admin/` - Admin area (Disallowed)
- `GET /api/` - API endpoints (Disallowed, except /api/public/ for Googlebot)

### Testing
- `GET /crawl-delay-test` - Crawl delay testing page

## Robots.txt Rules

### Default User-Agent (*)
```
Allow: /
Allow: /public/
Allow: /blog/
Disallow: /private/
Disallow: /admin/
Disallow: /api/
Disallow: /temp/
Crawl-delay: 1
```

### Googlebot
```
Allow: /
Allow: /api/public/
Disallow: /private/
Crawl-delay: 0  # No delay
```

### Bingbot
```
Allow: /
Disallow: /private/
Disallow: /admin/
Crawl-delay: 2  # 2 second delay
```

### BadBot
```
Disallow: /  # Complete block
```

## Sitemap Structure

**sitemap-index.xml** points to:
1. **sitemap-main.xml**: Homepage, public, about, contact (4 URLs)
2. **sitemap-blog.xml**: 20 blog posts
3. **sitemap-products.xml**: 30 product pages

Total URLs in sitemaps: 54

## Testing

```bash
# View robots.txt
curl http://localhost:5006/robots.txt

# View sitemap index
curl http://localhost:5006/sitemap-index.xml

# View specific sitemap
curl http://localhost:5006/sitemap-blog.xml

# Test allowed page
curl http://localhost:5006/public/

# Test blocked page (returns page but shouldn't be crawled)
curl http://localhost:5006/private/

# Test crawl delay
curl http://localhost:5006/crawl-delay-test

# Test blog post
curl http://localhost:5006/blog/post-1

# Test product
curl http://localhost:5006/products/item-1
```

## Crawl Delays

Different bots experience different rate limits:
- **Default**: 1 second between requests
- **Googlebot**: No delay (0 seconds)
- **Bingbot**: 2 seconds between requests
- **BadBot**: Completely blocked

## Best Practices Demonstrated

1. **Multiple Sitemaps**: Organized by content type
2. **Sitemap Index**: Points to all sitemaps in one file
3. **User-Agent Rules**: Specific rules for different crawlers
4. **Allow Before Disallow**: More specific Allow rules override Disallow
5. **Crawl-Delay**: Rate limiting to prevent server overload
6. **Complete Block**: How to block malicious bots
