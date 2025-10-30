# Happy Path Site - Event Listings with JSON-LD

FastAPI application demonstrating proper event markup with Schema.org JSON-LD.

## Features

- **100 Events**: Generated with Faker (seed=42) for deterministic data
- **Pagination**: 10 events per page, 10 pages total
- **JSON-LD Markup**: Proper Schema.org Event structured data on each event page
- **SEO-Friendly**: robots.txt and sitemap.xml included
- **Event Details**: Full location, organizer, date/time information

## Running the Site

### Development
```bash
pip install -r requirements.txt
python app.py
```

### Docker
```bash
docker build -t happy-path-site .
docker run -p 5001:5001 happy-path-site
```

Visit: http://localhost:5001

## Endpoints

- `GET /` - Paginated event listings (?page=1-10)
- `GET /event/{id}` - Individual event detail with JSON-LD (id: 1-100)
- `GET /robots.txt` - Robots file
- `GET /sitemap.xml` - XML sitemap with all events

## Testing

```bash
# Test homepage
curl http://localhost:5001/

# Test pagination
curl http://localhost:5001/?page=2

# Test event detail
curl http://localhost:5001/event/1

# Test robots.txt
curl http://localhost:5001/robots.txt

# Test sitemap
curl http://localhost:5001/sitemap.xml
```

## JSON-LD Example

Each event page includes structured data like:

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Event Name",
  "description": "Event description",
  "startDate": "2025-11-01T00:00:00",
  "endDate": "2025-11-01T03:00:00",
  "location": {
    "@type": "Place",
    "name": "Venue Name",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "123 Main St",
      "addressLocality": "City",
      "addressRegion": "State",
      "postalCode": "12345",
      "addressCountry": "US"
    }
  },
  "organizer": {
    "@type": "Organization",
    "name": "Organizer Name",
    "url": "https://happy-path.site/organizer/1"
  }
}
```

## Sitemap Structure

- Homepage and 10 pagination pages (priority: 0.8-1.0)
- 100 individual event pages (priority: 0.6)
- Total URLs: 111
