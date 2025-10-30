from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration flag for crawlers
CRAWL_CONFIG = {
    "html_only": False,  # Set to True to only crawl HTML, False to include all resources
    "full_resources": True  # Full resource download including images, fonts, etc.
}

@app.get("/", response_class=HTMLResponse)
async def index():
    """Index page with links to various resource types"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Media & Non-HTML Test Site</title>
        <link rel="stylesheet" href="/static/css/styles.css">
        <link rel="preload" href="/static/fonts/test-font.woff2" as="font" type="font/woff2" crossorigin>
        <script src="/static/js/main.js" defer></script>
    </head>
    <body>
        <div class="container">
            <h1>📦 Media & Non-HTML Resource Test Site</h1>
            <p class="intro">This site tests crawler behavior with various resource types.</p>

            <section class="config-info">
                <h2>⚙️ Crawler Configuration</h2>
                <div class="config-box">
                    <p><strong>html_only:</strong> <span class="value">false</span> - Crawler should fetch all resources</p>
                    <p><strong>full_resources:</strong> <span class="value">true</span> - Download images, fonts, CSS, JS</p>
                </div>
            </section>

            <section class="resource-section">
                <h2>🎨 CSS Resources</h2>
                <ul>
                    <li><a href="/static/css/styles.css">styles.css</a> - Main stylesheet (already linked in head)</li>
                    <li><a href="/static/css/print.css">print.css</a> - Print stylesheet</li>
                </ul>
            </section>

            <section class="resource-section">
                <h2>📜 JavaScript Resources</h2>
                <ul>
                    <li><a href="/static/js/main.js">main.js</a> - Main script (already linked in head)</li>
                    <li><a href="/static/js/analytics.js">analytics.js</a> - Analytics script</li>
                </ul>
            </section>

            <section class="resource-section">
                <h2>🖼️ Image Resources</h2>
                <div class="image-gallery">
                    <div class="image-card">
                        <img src="/static/images/test-image.png" alt="PNG Test Image" width="200">
                        <p><a href="/static/images/test-image.png">test-image.png</a></p>
                    </div>
                    <div class="image-card">
                        <img src="/static/images/test-image.jpg" alt="JPG Test Image" width="200">
                        <p><a href="/static/images/test-image.jpg">test-image.jpg</a></p>
                    </div>
                    <div class="image-card">
                        <img src="/static/images/test-image.webp" alt="WebP Test Image" width="200">
                        <p><a href="/static/images/test-image.webp">test-image.webp</a></p>
                    </div>
                </div>
            </section>

            <section class="resource-section">
                <h2>🔤 Font Resources</h2>
                <p class="custom-font">This text uses a custom WOFF2 font.</p>
                <ul>
                    <li><a href="/static/fonts/test-font.woff2">test-font.woff2</a> - Web font</li>
                </ul>
            </section>

            <section class="resource-section">
                <h2>📄 Additional Pages</h2>
                <ul>
                    <li><a href="/page2">Page 2 - More Resources</a></li>
                    <li><a href="/config">Configuration Endpoint</a></li>
                </ul>
            </section>

            <footer>
                <p>Test different crawler modes: HTML-only vs Full resource download</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/page2", response_class=HTMLResponse)
async def page2():
    """Second page with additional resources"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Page 2 - Media Test</title>
        <link rel="stylesheet" href="/static/css/styles.css">
        <link rel="stylesheet" href="/static/css/print.css" media="print">
        <script src="/static/js/analytics.js" async></script>
    </head>
    <body>
        <div class="container">
            <h1>📄 Page 2: Additional Resources</h1>

            <section class="resource-section">
                <h2>Background Images (CSS)</h2>
                <div class="bg-image-box" style="background-image: url('/static/images/test-image.jpg'); height: 200px; background-size: cover;">
                    <p style="color: white; text-shadow: 2px 2px 4px black; padding: 20px;">
                        This div has a background image from CSS
                    </p>
                </div>
            </section>

            <section class="resource-section">
                <h2>Inline Styles & Scripts</h2>
                <div id="dynamic-content">
                    <p>This content is styled with inline CSS and may be modified by inline JavaScript.</p>
                </div>
                <script>
                    document.getElementById('dynamic-content').innerHTML += '<p>✓ JavaScript executed successfully!</p>';
                </script>
            </section>

            <section class="resource-section">
                <h2>External Resources</h2>
                <ul>
                    <li>CSS files loaded: 2</li>
                    <li>JS files loaded: 1</li>
                    <li>Images displayed: 4</li>
                    <li>Fonts loaded: 1</li>
                </ul>
            </section>

            <p><a href="/">← Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/config")
async def config():
    """Return crawler configuration"""
    return CRAWL_CONFIG

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5010)
