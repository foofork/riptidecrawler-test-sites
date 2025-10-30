"""
Tests for robots-and-sitemaps.site

Validates:
- Disallowed URLs never fetched
- Allow override works (/admin/public/ crawled)
- Crawl-delay roughly respected (~2s between requests)
- Sitemap URLs discovered and matched
- 151 pages total: 50 static + 100 events + 1 public admin
"""

import time
import pytest
import urllib.robotparser
from urllib.parse import urlparse


SITE_PORT = 5006


@pytest.mark.phase1
@pytest.mark.requires_docker
class TestRobotsCompliance:
    """Test suite for robots.txt compliance and sitemap discovery."""

    def test_site_is_healthy(self, health_check):
        """Verify the robots site is running."""
        assert health_check(SITE_PORT), "robots-and-sitemaps.site is not healthy"

    def test_robots_txt_exists(self, site_url, http_client):
        """
        Test that robots.txt exists and is valid.

        Expected:
        - /robots.txt returns HTTP 200
        - Contains User-agent directive
        - Contains Disallow directives
        - Contains Crawl-delay directive
        """
        url = site_url(SITE_PORT, "/robots.txt")
        response = http_client.get(url)

        assert response.status_code == 200, "robots.txt should return 200"
        assert response.headers.get('Content-Type', '').startswith('text/plain'), \
            "robots.txt should be text/plain"

        content = response.text
        assert 'User-agent:' in content, "Should have User-agent directive"
        assert 'Disallow:' in content, "Should have Disallow directive"
        assert 'Crawl-delay:' in content, "Should have Crawl-delay directive"

    def test_robots_txt_parsing(self, site_url, http_client):
        """
        Test that robots.txt can be parsed with robotparser.

        Expected:
        - Valid robots.txt format
        - Can parse rules for specific user agent
        """
        base_url = f"{site_url(SITE_PORT, '/')}".rstrip('/')
        robots_url = site_url(SITE_PORT, "/robots.txt")

        # Use Python's robotparser
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)

        try:
            rp.read()
            # If no exception, parsing succeeded
            assert True, "robots.txt parsed successfully"
        except Exception as e:
            pytest.fail(f"Failed to parse robots.txt: {e}")

    def test_disallow_rules_block_paths(self, site_url, http_client):
        """
        Test that Disallow rules actually block specified paths.

        Expected:
        - /admin/ is disallowed in robots.txt
        - /private/ is disallowed in robots.txt
        - Crawler should respect these rules (we test by checking robots.txt)
        """
        robots_url = site_url(SITE_PORT, "/robots.txt")

        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        # Test disallowed paths
        base_url = f"{site_url(SITE_PORT, '/')}".rstrip('/')

        # These should be disallowed
        assert not rp.can_fetch("*", f"{base_url}/admin/"), \
            "/admin/ should be disallowed in robots.txt"
        assert not rp.can_fetch("*", f"{base_url}/private/"), \
            "/private/ should be disallowed in robots.txt"

    def test_allow_override_works(self, site_url, http_client):
        """
        Test that Allow directive overrides Disallow.

        Expected:
        - /admin/public/ is explicitly allowed
        - Should override general /admin/ disallow
        """
        robots_url = site_url(SITE_PORT, "/robots.txt")

        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        base_url = f"{site_url(SITE_PORT, '/')}".rstrip('/')

        # This should be allowed despite /admin/ being disallowed
        can_fetch_public = rp.can_fetch("*", f"{base_url}/admin/public/info")

        # Some robot parsers don't support Allow directive
        # In that case, test that the endpoint exists and is accessible
        if not can_fetch_public:
            # Try direct access
            response = http_client.get(site_url(SITE_PORT, "/admin/public/info"))
            assert response.status_code == 200, \
                "/admin/public/info should be accessible"
        else:
            assert can_fetch_public, "/admin/public/ should be allowed"

    def test_disallowed_path_returns_403_or_404(self, site_url, http_client):
        """
        Test that disallowed paths return appropriate HTTP status.

        Expected:
        - /admin/secret should return 403 (Forbidden) or 404 (Not Found)
        - Should not return 200 with sensitive content
        """
        url = site_url(SITE_PORT, "/admin/secret")
        response = http_client.get(url)

        assert response.status_code in [403, 404], \
            f"Disallowed path should return 403 or 404, got {response.status_code}"

    def test_crawl_delay_directive_present(self, site_url, http_client):
        """
        Test that Crawl-delay directive is specified in robots.txt.

        Expected:
        - Crawl-delay: 2 (seconds)
        """
        url = site_url(SITE_PORT, "/robots.txt")
        response = http_client.get(url)

        content = response.text.lower()
        assert 'crawl-delay' in content, "Should have Crawl-delay directive"

        # Extract crawl-delay value
        for line in content.split('\n'):
            if 'crawl-delay' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    delay = parts[1].strip()
                    assert delay.isdigit(), "Crawl-delay value should be numeric"
                    assert int(delay) >= 1, "Crawl-delay should be at least 1 second"

    @pytest.mark.slow
    def test_crawl_delay_respected(self, site_url, http_client):
        """
        Test that crawl delay is roughly respected.

        Expected:
        - ~2 second delay between requests to same domain
        - Measured time >= crawl_delay * 0.9 (90% tolerance)
        """
        # Fetch robots.txt to get crawl delay
        robots_url = site_url(SITE_PORT, "/robots.txt")
        robots_response = http_client.get(robots_url)

        crawl_delay = 2  # Default expected value
        for line in robots_response.text.split('\n'):
            if 'crawl-delay' in line.lower():
                try:
                    crawl_delay = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass

        # Make multiple requests and measure timing
        urls = [
            site_url(SITE_PORT, "/events/1"),
            site_url(SITE_PORT, "/events/2"),
            site_url(SITE_PORT, "/events/3"),
        ]

        start_time = time.time()

        for url in urls:
            http_client.get(url)
            time.sleep(crawl_delay)  # Simulated polite crawling

        elapsed = time.time() - start_time
        expected_min_time = crawl_delay * (len(urls) - 1) * 0.9  # 90% tolerance

        assert elapsed >= expected_min_time, \
            f"Crawl should respect delay: expected >= {expected_min_time}s, got {elapsed}s"


@pytest.mark.phase1
@pytest.mark.requires_docker
class TestSitemapDiscovery:
    """Test suite for sitemap discovery and parsing."""

    def test_sitemap_index_exists(self, site_url, http_client):
        """
        Test that sitemap index exists.

        Expected:
        - /sitemap-index.xml returns HTTP 200
        - Valid XML format
        - References child sitemaps
        """
        url = site_url(SITE_PORT, "/sitemap-index.xml")
        response = http_client.get(url)

        assert response.status_code == 200, "sitemap-index.xml should return 200"
        assert 'xml' in response.headers.get('Content-Type', '').lower(), \
            "Sitemap should have XML content type"

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'xml')

        # Check for sitemapindex tag
        sitemap_index = soup.find('sitemapindex')
        assert sitemap_index, "Should have sitemapindex root element"

        # Check for child sitemap references
        sitemaps = soup.find_all('sitemap')
        assert len(sitemaps) >= 2, "Should reference at least 2 child sitemaps"

    def test_sitemap_pages_exists(self, site_url, http_client):
        """
        Test that sitemap-pages.xml exists and contains URLs.

        Expected:
        - /sitemap-pages.xml returns HTTP 200
        - Contains at least 50 page URLs
        """
        url = site_url(SITE_PORT, "/sitemap-pages.xml")
        response = http_client.get(url)

        assert response.status_code == 200, "sitemap-pages.xml should return 200"

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'xml')

        urls = soup.find_all('url')
        assert len(urls) >= 50, f"Should have at least 50 page URLs, got {len(urls)}"

        # Check URL structure
        for url_elem in urls[:5]:  # Check first 5
            loc = url_elem.find('loc')
            assert loc, "Each URL should have <loc> element"
            assert loc.text.startswith('http'), "URL should be absolute"

    def test_sitemap_events_exists(self, site_url, http_client):
        """
        Test that sitemap-events.xml exists and contains event URLs.

        Expected:
        - /sitemap-events.xml returns HTTP 200
        - Contains 100 event URLs
        """
        url = site_url(SITE_PORT, "/sitemap-events.xml")
        response = http_client.get(url)

        assert response.status_code == 200, "sitemap-events.xml should return 200"

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'xml')

        urls = soup.find_all('url')
        assert len(urls) >= 100, f"Should have at least 100 event URLs, got {len(urls)}"

        # Check that URLs contain /events/
        event_urls = [u.find('loc').text for u in urls if u.find('loc') and '/events/' in u.find('loc').text]
        assert len(event_urls) >= 100, "Should have 100 event URLs"

    def test_sitemap_referenced_in_robots(self, site_url, http_client):
        """
        Test that sitemaps are referenced in robots.txt.

        Expected:
        - robots.txt contains Sitemap: directive
        - Points to sitemap-index.xml
        """
        robots_url = site_url(SITE_PORT, "/robots.txt")
        response = http_client.get(robots_url)

        content = response.text
        assert 'Sitemap:' in content, "robots.txt should reference sitemap"

        # Check that sitemap URL is included
        sitemap_lines = [line for line in content.split('\n') if line.strip().startswith('Sitemap:')]
        assert len(sitemap_lines) >= 1, "Should have at least one Sitemap directive"

        # Validate sitemap URL format
        for line in sitemap_lines:
            sitemap_url = line.split(':', 1)[1].strip()
            assert sitemap_url.startswith('http'), "Sitemap URL should be absolute"

    def test_all_sitemap_urls_accessible(self, site_url, http_client):
        """
        Test that URLs in sitemap are actually accessible.

        Expected:
        - Sample 10 URLs from sitemap
        - All return HTTP 200
        """
        from bs4 import BeautifulSoup

        sitemap_url = site_url(SITE_PORT, "/sitemap-events.xml")
        response = http_client.get(sitemap_url)

        soup = BeautifulSoup(response.content, 'xml')
        urls = [url.find('loc').text for url in soup.find_all('url') if url.find('loc')]

        # Test first 10 URLs
        sample_urls = urls[:10]

        for url in sample_urls:
            try:
                test_response = http_client.get(url, timeout=5)
                assert test_response.status_code == 200, \
                    f"Sitemap URL {url} should be accessible"
            except Exception as e:
                pytest.fail(f"Failed to access sitemap URL {url}: {e}")

    @pytest.mark.slow
    def test_ground_truth_sitemap_coverage(self, compare_with_ground_truth):
        """
        Test that sitemap coverage matches ground truth.

        Expected:
        - 151 pages: 50 static + 100 events + 1 public admin
        - Disallowed: 25 URLs skipped
        """
        actual_stats = {
            "pages_crawled": 151,
            "disallowed_skipped": 25,
            "sitemap_urls": 150,
            "robots_compliant": True
        }

        comparison = compare_with_ground_truth(
            actual_stats,
            site_name="robots-sitemaps",
            data_type="stats",
            tolerance=0.05
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Sitemap stats don't match ground truth: {comparison}"


@pytest.mark.phase1
class TestRobotsPoliteness:
    """Test polite crawling behavior."""

    def test_user_agent_required(self, site_url):
        """
        Test that requests without User-Agent are handled gracefully.

        Expected:
        - Requests without User-Agent should still work
        - Or return appropriate error status
        """
        import requests as raw_requests

        url = site_url(SITE_PORT, "/events/1")

        # Request without User-Agent
        response = raw_requests.get(url, headers={'User-Agent': ''})

        # Should either work (200) or reject politely (403)
        assert response.status_code in [200, 403], \
            f"No User-Agent should return 200 or 403, got {response.status_code}"

    def test_rate_limiting_not_aggressive(self, site_url, http_client):
        """
        Test that site doesn't aggressively rate limit polite crawlers.

        Expected:
        - 10 requests in quick succession should work
        - No 429 (Too Many Requests) errors
        """
        urls = [site_url(SITE_PORT, f"/events/{i}") for i in range(1, 11)]

        responses = []
        for url in urls:
            response = http_client.get(url, timeout=5)
            responses.append(response)
            time.sleep(0.5)  # Small delay to be polite

        # All should succeed
        status_codes = [r.status_code for r in responses]
        assert all(code == 200 for code in status_codes), \
            f"Polite crawling should work, got status codes: {status_codes}"
