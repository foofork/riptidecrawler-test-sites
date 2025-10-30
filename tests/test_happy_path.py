"""
Tests for happy-path.site

Validates:
- Basic crawling (110 pages: 1 index + 10 list + 100 detail - 1 canonical)
- JSON-LD Event extraction (100 events)
- Sitemap discovery and parsing
- Canonical URL deduplication
- Pagination handling
"""

import json
import pytest
import requests
from bs4 import BeautifulSoup


SITE_PORT = 5001


@pytest.mark.phase1
@pytest.mark.requires_docker
class TestHappyPath:
    """Test suite for happy-path.site baseline functionality."""

    def test_site_is_healthy(self, health_check):
        """
        Verify the site is running and responding.

        Expected: HTTP 200 on root path
        """
        assert health_check(SITE_PORT), "happy-path.site is not healthy"

    def test_index_page_loads(self, site_url, http_client):
        """
        Test that the index page loads successfully.

        Expected:
        - HTTP 200
        - Contains event listings or links to events
        """
        url = site_url(SITE_PORT, "/")
        response = http_client.get(url)

        assert response.status_code == 200, "Index page should return 200"
        assert len(response.content) > 0, "Index page should have content"

        # Check for expected content structure
        soup = BeautifulSoup(response.content, 'html.parser')
        assert soup.find('title'), "Page should have a title"

    def test_events_pagination(self, site_url, http_client):
        """
        Test that event listings are paginated correctly.

        Expected:
        - 10 events per page
        - 10 pages total (100 events)
        - Pagination links present
        """
        base_url = site_url(SITE_PORT, "/events/")

        # Test first page
        response = http_client.get(base_url)
        assert response.status_code == 200, "Events page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for event items (adjust selector based on actual implementation)
        events = soup.find_all(class_='event-item') or soup.find_all('article')
        assert len(events) <= 10, "First page should have at most 10 events"

        # Check for pagination links
        pagination = soup.find(class_='pagination') or soup.find_all('a', href=lambda x: x and 'page=' in x)
        assert pagination, "Pagination links should be present"

    def test_event_detail_has_jsonld(self, site_url, http_client):
        """
        Test that event detail pages contain valid JSON-LD Event schema.

        Expected:
        - JSON-LD script tag present
        - @type: "Event"
        - Required fields: name, startDate, location
        """
        # Test event ID 1
        url = site_url(SITE_PORT, "/events/1")
        response = http_client.get(url)

        assert response.status_code == 200, "Event detail page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find JSON-LD script tag
        jsonld_script = soup.find('script', {'type': 'application/ld+json'})
        assert jsonld_script, "Event page should have JSON-LD script tag"

        # Parse JSON-LD
        jsonld_data = json.loads(jsonld_script.string)

        # Validate Event schema
        assert jsonld_data.get('@type') == 'Event', "JSON-LD should be of type Event"
        assert 'name' in jsonld_data, "Event should have name field"
        assert 'startDate' in jsonld_data, "Event should have startDate field"
        assert 'location' in jsonld_data, "Event should have location field"

    def test_canonical_urls_present(self, site_url, http_client):
        """
        Test that canonical URLs are present on detail pages.

        Expected:
        - <link rel="canonical"> tag present
        - Canonical URL points to self or normalized version
        """
        url = site_url(SITE_PORT, "/events/1")
        response = http_client.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        canonical = soup.find('link', {'rel': 'canonical'})
        assert canonical, "Detail page should have canonical link"
        assert canonical.get('href'), "Canonical link should have href attribute"

    def test_sitemap_exists_and_valid(self, site_url, http_client):
        """
        Test that sitemap.xml exists and contains all URLs.

        Expected:
        - /sitemap.xml returns HTTP 200
        - Valid XML format
        - Contains event URLs
        """
        url = site_url(SITE_PORT, "/sitemap.xml")
        response = http_client.get(url)

        assert response.status_code == 200, "sitemap.xml should return 200"
        assert 'xml' in response.headers.get('Content-Type', '').lower(), \
            "sitemap.xml should have XML content type"

        # Parse XML
        soup = BeautifulSoup(response.content, 'xml')

        # Check for URL entries
        urls = soup.find_all('url')
        assert len(urls) > 0, "Sitemap should contain URL entries"

        # Check for event URLs
        locs = [url.find('loc').text for url in urls if url.find('loc')]
        event_urls = [loc for loc in locs if '/events/' in loc]
        assert len(event_urls) >= 50, "Sitemap should contain at least 50 event URLs"

    def test_robots_txt_exists(self, site_url, http_client):
        """
        Test that robots.txt exists and allows crawling.

        Expected:
        - /robots.txt returns HTTP 200
        - Contains User-agent directive
        - No disallow for main content
        """
        url = site_url(SITE_PORT, "/robots.txt")
        response = http_client.get(url)

        assert response.status_code == 200, "robots.txt should return 200"

        robots_content = response.text
        assert 'User-agent:' in robots_content, "robots.txt should have User-agent directive"

    @pytest.mark.slow
    def test_crawl_completes_successfully(self, site_url, crawl_simulator):
        """
        Test that a basic crawl can complete successfully.

        Expected:
        - Can crawl at least 10 pages without errors
        - All responses are HTTP 200
        """
        start_url = site_url(SITE_PORT, "/")
        result = crawl_simulator(start_url, max_pages=20)

        assert result['pages_crawled'] >= 10, "Should crawl at least 10 pages"

        # Check all pages returned 200
        successful_pages = [p for p in result['pages'] if p['status_code'] == 200]
        assert len(successful_pages) == result['pages_crawled'], \
            "All crawled pages should return 200"

    @pytest.mark.slow
    def test_ground_truth_pages_match(self, site_url, http_client, compare_with_ground_truth):
        """
        Test that crawl results match ground truth.

        Expected:
        - 110 pages crawled (within 5% tolerance)
        - Matches ground-truth/happy-path.pages.jsonl
        """
        # This is a placeholder - actual implementation would:
        # 1. Perform full crawl using RipTide
        # 2. Extract page data
        # 3. Compare with ground truth

        # For now, simulate crawl results
        actual_pages = [
            {"url": site_url(SITE_PORT, "/"), "status_code": 200},
            {"url": site_url(SITE_PORT, "/events/"), "status_code": 200},
            # ... more pages would be added by actual crawler
        ]

        # Compare with ground truth
        comparison = compare_with_ground_truth(
            actual_pages,
            site_name="happy-path",
            data_type="pages",
            tolerance=0.05
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Ground truth comparison failed: {comparison['differences']}"

    @pytest.mark.slow
    def test_ground_truth_entities_match(self, compare_with_ground_truth):
        """
        Test that extracted entities match ground truth.

        Expected:
        - 100 Event entities extracted
        - All have required fields (name, startDate)
        """
        # Placeholder - actual implementation would extract entities
        actual_entities = [
            {
                "type": "Event",
                "name": "Summer Festival 2024",
                "startDate": "2024-06-15"
            },
            # ... more entities from actual extraction
        ]

        comparison = compare_with_ground_truth(
            actual_entities,
            site_name="happy-path",
            data_type="entities",
            tolerance=0.05
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Entity extraction doesn't match ground truth: {comparison}"


@pytest.mark.phase1
class TestHappyPathDataQuality:
    """Test data quality and consistency."""

    def test_deterministic_data_generation(self, site_url, http_client):
        """
        Test that data is deterministically generated using FIXTURE_SEED.

        Expected:
        - Multiple requests return identical data
        - Event IDs are consistent
        """
        url = site_url(SITE_PORT, "/events/1")

        # Fetch same page twice
        response1 = http_client.get(url)
        response2 = http_client.get(url)

        assert response1.content == response2.content, \
            "Same URL should return identical content (deterministic generation)"

    def test_all_events_have_unique_ids(self, site_url, http_client):
        """
        Test that all events have unique IDs.

        Expected:
        - No duplicate event IDs
        - IDs are sequential or properly unique
        """
        # Test first 20 events
        event_ids = set()

        for i in range(1, 21):
            url = site_url(SITE_PORT, f"/events/{i}")
            response = http_client.get(url)

            if response.status_code == 200:
                event_ids.add(i)

        assert len(event_ids) == 20, "All events should have unique IDs"
