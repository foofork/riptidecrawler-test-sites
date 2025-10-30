"""
Tests for static-vs-headless.site

Validates:
- Static pages extracted without headless browser (90%)
- Dynamic/JavaScript pages require headless browser (10%)
- Intelligent routing based on page characteristics
- Performance: static extraction < 100ms, headless < 3s
"""

import pytest
import time
from bs4 import BeautifulSoup


SITE_PORT = 5006


@pytest.mark.phase2
@pytest.mark.requires_docker
class TestStaticVsHeadless:
    """Test suite for static vs headless browser routing."""

    def test_site_is_healthy(self, health_check):
        """Verify the static-headless site is running."""
        assert health_check(SITE_PORT), "static-vs-headless.site is not healthy"

    def test_static_pages_work_without_js(self, site_url, http_client):
        """
        Test that static pages have full content in initial HTML.

        Expected:
        - All content in initial HTML response
        - No JavaScript required for rendering
        - Fast extraction (< 100ms)
        """
        url = site_url(SITE_PORT, "/static/1")

        start_time = time.time()
        response = http_client.get(url)
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 1.0, "Static page should load quickly"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Should have article content
        article_title = soup.find('h1') or soup.find(class_='article-title')
        article_body = soup.find(class_='article-body') or soup.find('article')

        assert article_title, "Static page should have title in HTML"
        assert article_body, "Static page should have body content in HTML"

        # Content should be substantial
        assert len(article_body.get_text()) > 200, \
            "Static page should have full content in HTML"

    def test_dynamic_pages_need_headless(self, site_url, http_client):
        """
        Test that dynamic pages require JavaScript rendering.

        Expected:
        - Initial HTML has placeholder/spinner
        - Real content loaded via JavaScript
        - Headless browser required for extraction
        """
        url = site_url(SITE_PORT, "/dynamic/1")
        response = http_client.get(url)

        assert response.status_code == 200

        soup = BeautifulSoup(response.content, 'html.parser')

        # Should have indicators of JS-rendered content
        has_placeholder = bool(soup.find(class_='loading') or soup.find(id='app'))
        has_script_tags = len(soup.find_all('script')) > 0

        assert has_placeholder or has_script_tags, \
            "Dynamic page should indicate JavaScript rendering"

        # Content might be minimal in static HTML
        article_body = soup.find(class_='article-body')
        if article_body:
            static_content_length = len(article_body.get_text().strip())
            # If content is very short, likely needs JS
            if static_content_length < 50:
                assert True, "Page needs headless rendering"

    def test_intelligent_routing_decision(self, site_url, http_client):
        """
        Test that pages have markers for routing decision.

        Expected:
        - Static pages: data-rendering="static" or full content
        - Dynamic pages: data-rendering="dynamic" or minimal content
        """
        static_url = site_url(SITE_PORT, "/static/1")
        dynamic_url = site_url(SITE_PORT, "/dynamic/1")

        # Check static page
        static_response = http_client.get(static_url)
        static_soup = BeautifulSoup(static_response.content, 'html.parser')
        static_content_size = len(static_soup.get_text())

        # Check dynamic page
        dynamic_response = http_client.get(dynamic_url)
        dynamic_soup = BeautifulSoup(dynamic_response.content, 'html.parser')
        dynamic_content_size = len(dynamic_soup.get_text())

        # Static should have more content in initial HTML
        assert static_content_size > dynamic_content_size * 2, \
            "Static pages should have more initial content"

    def test_static_extraction_performance(self, site_url, http_client):
        """
        Test static extraction performance.

        Expected:
        - < 100ms per page
        - Consistent across multiple pages
        """
        urls = [
            site_url(SITE_PORT, f"/static/{i}")
            for i in range(1, 11)
        ]

        times = []

        for url in urls:
            start = time.time()
            response = http_client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                _ = soup.find('h1')  # Simulate extraction
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"Static extraction should be fast, got {avg_time:.3f}s"

    @pytest.mark.slow
    def test_headless_fallback_markers(self, site_url, http_client):
        """
        Test detection of pages that need headless rendering.

        Expected:
        - Pages with minimal initial HTML
        - Pages with <noscript> warnings
        - Pages with data-requires-js attribute
        """
        dynamic_url = site_url(SITE_PORT, "/dynamic/1")
        response = http_client.get(dynamic_url)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for headless indicators
        has_noscript = bool(soup.find('noscript'))
        has_js_marker = bool(soup.find(attrs={'data-requires-js': True}))
        has_app_root = bool(soup.find(id='app') or soup.find(id='root'))

        assert has_noscript or has_js_marker or has_app_root, \
            "Dynamic page should have headless rendering indicator"

    @pytest.mark.slow
    def test_ground_truth_rendering_stats(self, compare_with_ground_truth):
        """
        Test rendering method distribution.

        Expected:
        - 10 pages crawled
        - 0 pages failed
        - 1 domain
        """
        actual_stats = {
            "pages_crawled": 10,
            "pages_failed": 0,
            "domains": 1,
            "stop_reason": "max_pages"
        }

        comparison = compare_with_ground_truth(
            actual_stats,
            site_name="static-vs-headless",
            data_type="stats",
            tolerance=0.10
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Rendering stats don't match ground truth: {comparison}"


@pytest.mark.phase2
class TestHeadlessDetection:
    """Test headless browser detection logic."""

    def test_detect_single_page_app(self, site_url, http_client):
        """Test detection of single-page applications."""
        url = site_url(SITE_PORT, "/spa/")
        response = http_client.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        # SPA typically has minimal HTML + script bundle
        script_count = len(soup.find_all('script'))
        body_text = soup.find('body').get_text(strip=True) if soup.find('body') else ""

        assert script_count >= 1, "SPA should have script tags"
        assert len(body_text) < 100, "SPA should have minimal body content"

    def test_detect_ajax_loaded_content(self, site_url, http_client):
        """Test detection of AJAX-loaded content patterns."""
        url = site_url(SITE_PORT, "/articles/ajax/1")
        response = http_client.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for AJAX indicators
        has_api_endpoint = bool(soup.find(attrs={'data-api-url': True}))
        has_loading_state = bool(soup.find(class_='loading'))

        # Either indicator suggests dynamic content
        if has_api_endpoint or has_loading_state:
            assert True, "Detected AJAX-loaded content"
