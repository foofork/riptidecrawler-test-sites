from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ===== 301 PERMANENT REDIRECTS =====

@app.get("/redirect/301/{n}")
async def redirect_301(n: int):
    """Redirect with 301 (Permanent)"""
    if n <= 1:
        return RedirectResponse(url="/final", status_code=301)
    return RedirectResponse(url=f"/redirect/301/{n-1}", status_code=301)

@app.get("/absolute-redirect/301/{n}")
async def absolute_redirect_301(n: int):
    """Absolute URL redirect with 301"""
    if n <= 1:
        return RedirectResponse(url="https://redirects-canonical.site/final", status_code=301)
    return RedirectResponse(url=f"https://redirects-canonical.site/absolute-redirect/301/{n-1}", status_code=301)

# ===== 302 TEMPORARY REDIRECTS =====

@app.get("/redirect/302/{n}")
async def redirect_302(n: int):
    """Redirect with 302 (Temporary)"""
    if n <= 1:
        return RedirectResponse(url="/final", status_code=302)
    return RedirectResponse(url=f"/redirect/302/{n-1}", status_code=302)

@app.get("/absolute-redirect/302/{n}")
async def absolute_redirect_302(n: int):
    """Absolute URL redirect with 302"""
    if n <= 1:
        return RedirectResponse(url="https://redirects-canonical.site/final", status_code=302)
    return RedirectResponse(url=f"https://redirects-canonical.site/absolute-redirect/302/{n-1}", status_code=302)

# ===== REDIRECT CHAINS =====

@app.get("/chain/start")
async def chain_start():
    """Start of a 3-hop redirect chain"""
    return RedirectResponse(url="/chain/middle", status_code=301)

@app.get("/chain/middle")
async def chain_middle():
    """Middle of redirect chain"""
    return RedirectResponse(url="/chain/final", status_code=302)

@app.get("/chain/final")
async def chain_final(request: Request):
    """End of redirect chain"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Redirect Chain Complete",
        "content": "You've successfully followed a 3-hop redirect chain!",
        "path": "/chain/final"
    })

# ===== CANONICAL URLs =====

@app.get("/canonical/original")
async def canonical_original(request: Request):
    """Original page with canonical URL"""
    return templates.TemplateResponse("canonical.html", {
        "request": request,
        "title": "Original Canonical Page",
        "canonical_url": "https://redirects-canonical.site/canonical/original",
        "content": "This is the canonical version of the page."
    })

@app.get("/canonical/duplicate1")
async def canonical_duplicate1(request: Request):
    """Duplicate page pointing to canonical"""
    return templates.TemplateResponse("canonical.html", {
        "request": request,
        "title": "Duplicate Page 1",
        "canonical_url": "https://redirects-canonical.site/canonical/original",
        "content": "This is a duplicate page that points to the canonical version."
    })

@app.get("/canonical/duplicate2")
async def canonical_duplicate2(request: Request):
    """Another duplicate page pointing to canonical"""
    return templates.TemplateResponse("canonical.html", {
        "request": request,
        "title": "Duplicate Page 2",
        "canonical_url": "https://redirects-canonical.site/canonical/original",
        "content": "This is another duplicate page that points to the canonical version."
    })

# ===== MIXED REDIRECT TYPES =====

@app.get("/mixed-chain/start")
async def mixed_chain_start():
    """Start of mixed 301/302 chain"""
    return RedirectResponse(url="/mixed-chain/step2", status_code=301)

@app.get("/mixed-chain/step2")
async def mixed_chain_step2():
    """Middle step with 302"""
    return RedirectResponse(url="/mixed-chain/final", status_code=302)

@app.get("/mixed-chain/final")
async def mixed_chain_final(request: Request):
    """End of mixed chain"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Mixed Chain Complete",
        "content": "You've followed a mixed 301→302 redirect chain!",
        "path": "/mixed-chain/final"
    })

# ===== FINAL DESTINATIONS =====

@app.get("/final")
async def final(request: Request):
    """Final destination for redirects"""
    return templates.TemplateResponse("page.html", {
        "request": request,
        "title": "Final Destination",
        "content": "You've reached the final destination!",
        "path": "/final"
    })

# ===== HOME & DOCUMENTATION =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with test links"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/robots.txt", response_class=Response)
async def robots():
    """Robots.txt file"""
    content = """User-agent: *
Allow: /
Disallow: /redirect/
Disallow: /chain/start
Disallow: /mixed-chain/start

Sitemap: https://redirects-canonical.site/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    """XML sitemap"""
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://redirects-canonical.site/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://redirects-canonical.site/canonical/original</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://redirects-canonical.site/final</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://redirects-canonical.site/chain/final</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""

    return Response(content=sitemap_xml, media_type="application/xml")

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {
        "status": "healthy",
        "service": "redirects-canonical.site",
        "port": 5005,
        "features": ["301_redirects", "302_redirects", "canonical_urls", "redirect_chains"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
