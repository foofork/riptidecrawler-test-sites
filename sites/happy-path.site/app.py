from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from faker import Faker
from datetime import datetime, timedelta
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Faker with seed for deterministic data
fake = Faker()
Faker.seed(42)

# Generate 100 events (10 pages * 10 events)
def generate_events(count=100):
    events = []
    base_date = datetime(2025, 11, 1)

    for i in range(count):
        event_date = base_date + timedelta(days=i % 30)
        event = {
            "id": i + 1,
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "startDate": event_date.isoformat(),
            "endDate": (event_date + timedelta(hours=3)).isoformat(),
            "location": {
                "@type": "Place",
                "name": fake.company(),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": fake.street_address(),
                    "addressLocality": fake.city(),
                    "addressRegion": fake.state_abbr(),
                    "postalCode": fake.zipcode(),
                    "addressCountry": "US"
                }
            },
            "organizer": {
                "@type": "Organization",
                "name": fake.company(),
                "url": f"https://happy-path.site/organizer/{i+1}"
            },
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode"
        }
        events.append(event)

    return events

EVENTS = generate_events()

def get_json_ld(event):
    """Generate JSON-LD for an event"""
    return {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event["name"],
        "description": event["description"],
        "startDate": event["startDate"],
        "endDate": event["endDate"],
        "location": event["location"],
        "organizer": event["organizer"],
        "eventStatus": event["eventStatus"],
        "eventAttendanceMode": event["eventAttendanceMode"],
        "url": f"https://happy-path.site/event/{event['id']}"
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, page: int = 1):
    """Home page with paginated event listings"""
    per_page = 10
    total_pages = 10

    # Validate page number
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    page_events = EVENTS[start_idx:end_idx]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "events": page_events,
        "current_page": page,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages
    })

@app.get("/event/{event_id}", response_class=HTMLResponse)
async def event_detail(request: Request, event_id: int):
    """Individual event detail page with JSON-LD"""
    if event_id < 1 or event_id > len(EVENTS):
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    event = EVENTS[event_id - 1]
    json_ld = get_json_ld(event)

    return templates.TemplateResponse("event.html", {
        "request": request,
        "event": event,
        "json_ld": json.dumps(json_ld, indent=2)
    })

@app.get("/robots.txt", response_class=Response)
async def robots():
    """Robots.txt file"""
    content = """User-agent: *
Allow: /
Sitemap: https://happy-path.site/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    """XML sitemap with all events"""
    urls = []

    # Homepage
    urls.append("""  <url>
    <loc>https://happy-path.site/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Pagination pages
    for page in range(1, 11):
        urls.append(f"""  <url>
    <loc>https://happy-path.site/?page={page}</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>""")

    # All events
    for event in EVENTS:
        urls.append(f"""  <url>
    <loc>https://happy-path.site/event/{event['id']}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    return Response(content=sitemap_xml, media_type="application/xml")

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {
        "status": "healthy",
        "service": "happy-path.site",
        "port": 5001,
        "events_count": len(EVENTS),
        "pages": 10
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
