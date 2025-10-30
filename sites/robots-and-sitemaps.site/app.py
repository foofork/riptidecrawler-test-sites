from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ===== ROBOTS.TXT TESTING =====

@app.get("/robots.txt", response_class=Response)
async def robots():
    """Complex robots.txt with various rules"""
    content = """# Main crawler rules
User-agent: *
Disallow: /private/
Disallow: /admin/
Disallow: /api/
Disallow: /temp/
Allow: /
Allow: /public/
Allow: /blog/
Crawl-delay: 1

# Google-specific rules
User-agent: Googlebot
Allow: /
Allow: /api/public/
Disallow: /private/
Crawl-delay: 0

# Bing-specific rules
User-agent: Bingbot
Allow: /
Disallow: /private/
Disallow: /admin/
Crawl-delay: 2

# Block bad bots
User-agent: BadBot
Disallow: /

# Sitemap locations
Sitemap: https://robots-and-sitemaps.site/sitemap-index.xml
Sitemap: https://robots-and-sitemaps.site/sitemap-main.xml
Sitemap: https://robots-and-sitemaps.site/sitemap-blog.xml
"""
    return Response(content=content, media_type="text/plain")

# ===== SITEMAP INDEX =====

@app.get("/sitemap-index.xml", response_class=Response)
async def sitemap_index():
    """Sitemap index pointing to multiple sitemaps"""
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://robots-and-sitemaps.site/sitemap-main.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://robots-and-sitemaps.site/sitemap-blog.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://robots-and-sitemaps.site/sitemap-products.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
</sitemapindex>"""

    return Response(content=sitemap_xml, media_type="application/xml")

# ===== INDIVIDUAL SITEMAPS =====

@app.get("/sitemap-main.xml", response_class=Response)
async def sitemap_main():
    """Main sitemap with core pages"""
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://robots-and-sitemaps.site/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://robots-and-sitemaps.site/public/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://robots-and-sitemaps.site/about</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://robots-and-sitemaps.site/contact</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""

    return Response(content=sitemap_xml, media_type="application/xml")

@app.get("/sitemap-blog.xml", response_class=Response)
async def sitemap_blog():
    """Blog sitemap"""
    urls = []
    for i in range(1, 21):
        urls.append(f"""  <url>
    <loc>https://robots-and-sitemaps.site/blog/post-{i}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    return Response(content=sitemap_xml, media_type="application/xml")

@app.get("/sitemap-products.xml", response_class=Response)
async def sitemap_products():
    """Products sitemap"""
    urls = []
    for i in range(1, 31):
        urls.append(f"""  <url>
    <loc>https://robots-and-sitemaps.site/products/item-{i}</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    return Response(content=sitemap_xml, media_type="application/xml")


@app.get("/sitemap-pages.xml", response_class=Response)
async def sitemap_pages():
    """Static pages sitemap with 50+ URLs"""
    urls = []

    # Main pages
    urls.append("""  <url>
    <loc>https://robots-and-sitemaps.site/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    urls.append("""  <url>
    <loc>https://robots-and-sitemaps.site/public/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    urls.append("""  <url>
    <loc>https://robots-and-sitemaps.site/blog/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

    # Add 50 static pages to meet test requirements
    for i in range(1, 51):
        urls.append(f"""  <url>
    <loc>https://robots-and-sitemaps.site/page/{i}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    return Response(content=sitemap_xml, media_type="application/xml")

# ===== TEST PAGES =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with test links"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/public/", response_class=HTMLResponse)
async def public_page(request: Request):
    """Allowed public page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Public Page",
        "content": "This page is allowed by robots.txt",
        "status": "✅ Crawlable"
    })

@app.get("/private/", response_class=HTMLResponse)
async def private_page(request: Request):
    """Disallowed private page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Private Page",
        "content": "This page is blocked by robots.txt",
        "status": "🚫 Not Crawlable"
    })

@app.get("/admin/", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Disallowed admin page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Admin Page",
        "content": "This page is blocked by robots.txt",
        "status": "🚫 Not Crawlable"
    })

@app.get("/api/", response_class=HTMLResponse)
async def api_page(request: Request):
    """Disallowed API endpoint"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "API Endpoint",
        "content": "This endpoint is blocked by robots.txt (except /api/public/ for Googlebot)",
        "status": "🚫 Not Crawlable (except Googlebot)"
    })

@app.get("/blog/", response_class=HTMLResponse)
async def blog_index(request: Request):
    """Blog index page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Blog Index",
        "content": "This page is allowed and included in sitemap-blog.xml",
        "status": "✅ Crawlable"
    })

@app.get("/blog/post-{post_id}")
async def blog_post(request: Request, post_id: int):
    """Individual blog post"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": f"Blog Post {post_id}",
        "content": f"This is blog post #{post_id}, included in sitemap-blog.xml",
        "status": "✅ Crawlable"
    })

@app.get("/products/item-{item_id}")
async def product_page(request: Request, item_id: int):
    """Product page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": f"Product {item_id}",
        "content": f"This is product #{item_id}, included in sitemap-products.xml",
        "status": "✅ Crawlable"
    })

@app.get("/about")
async def about(request: Request):
    """About page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "About Us",
        "content": "About page included in main sitemap",
        "status": "✅ Crawlable"
    })

@app.get("/contact")
async def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Contact",
        "content": "Contact page included in main sitemap",
        "status": "✅ Crawlable"
    })

# ===== CRAWL DELAY TESTING =====

@app.get("/crawl-delay-test")
async def crawl_delay_test(request: Request):
    """Page to test crawl-delay directive"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Crawl Delay Test",
        "content": "Test crawl-delay: 1 second for general crawlers, 0 for Googlebot, 2 for Bingbot",
        "status": "⏱️ Rate Limited"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {
        "status": "healthy",
        "service": "robots-and-sitemaps.site",
        "port": 5006,
        "features": ["robots.txt", "sitemap_index", "crawl_delay", "multiple_sitemaps"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5006)
