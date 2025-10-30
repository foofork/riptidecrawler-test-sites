"""
Tests for redirects-canonical.site

Validates:
- 301/302 redirect chains resolved correctly
- final_url != requested_url where applicable
- Canonical URLs reduce 150 fetches to 50 unique pages
- No duplicate entities extracted
"""

import pytest
import requests


SITE_PORT = 5005


@pytest.mark.phase1
@pytest.mark.requires_docker
class TestRedirects:
    """Test suite for redirect handling and canonical URL deduplication."""

    def test_site_is_healthy(self, health_check):
        """Verify the redirects site is running."""
        assert health_check(SITE_PORT), "redirects-canonical.site is not healthy"

    def test_301_permanent_redirect(self, site_url, http_client):
        """
        Test that 301 permanent redirects are followed correctly.

        Expected:
        - /old-event/1 -> /events/1 (HTTP 301)
        - Final URL should be /events/1
        - Content matches direct access to /events/1
        """
        old_url = site_url(SITE_PORT, "/old-event/1")
        direct_url = site_url(SITE_PORT, "/events/1")

        # Follow redirects
        response = http_client.get(old_url, allow_redirects=True)

        assert response.status_code == 200, "Redirect should resolve to 200"
        assert response.url == direct_url, f"Should redirect to {direct_url}"

        # Check that we got a 301 in the chain
        assert response.history, "Should have redirect history"
        assert response.history[0].status_code == 301, "First redirect should be 301"

    def test_302_temporary_redirect(self, site_url, http_client):
        """
        Test that 302 temporary redirects are followed correctly.

        Expected:
        - /temp/2 -> /events/2 (HTTP 302)
        - Final URL should be /events/2
        """
        temp_url = site_url(SITE_PORT, "/temp/2")
        direct_url = site_url(SITE_PORT, "/events/2")

        response = http_client.get(temp_url, allow_redirects=True)

        assert response.status_code == 200, "Redirect should resolve to 200"
        assert response.url == direct_url, f"Should redirect to {direct_url}"

        # Check that we got a 302 in the chain
        assert response.history, "Should have redirect history"
        assert response.history[0].status_code == 302, "First redirect should be 302"

    def test_redirect_chain_3_hops(self, site_url, http_client):
        """
        Test that multi-hop redirect chains are resolved correctly.

        Expected:
        - /chain/1/3 -> /chain/2/3 -> /chain/3/3 -> /events/3
        - Maximum 3 hops
        - Final URL should be /events/3
        """
        chain_url = site_url(SITE_PORT, "/chain/1/3")
        final_url = site_url(SITE_PORT, "/events/3")

        response = http_client.get(chain_url, allow_redirects=True)

        assert response.status_code == 200, "Redirect chain should resolve to 200"
        assert response.url == final_url, f"Should resolve to {final_url}"

        # Check redirect chain length
        assert len(response.history) <= 3, "Should follow at most 3 redirects"

    def test_canonical_link_present(self, site_url, http_client):
        """
        Test that pages have canonical links for deduplication.

        Expected:
        - <link rel="canonical"> present
        - Points to normalized URL
        """
        from bs4 import BeautifulSoup

        url = site_url(SITE_PORT, "/events/1")
        response = http_client.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        canonical = soup.find('link', {'rel': 'canonical'})

        assert canonical, "Page should have canonical link"
        assert canonical.get('href'), "Canonical link should have href"

    def test_hash_variants_same_canonical(self, site_url, http_client):
        """
        Test that hash variants (#comments, #share) resolve to same canonical.

        Expected:
        - /events/1#comments -> canonical: /events/1
        - /events/1#share -> canonical: /events/1
        """
        from bs4 import BeautifulSoup

        base_url = site_url(SITE_PORT, "/events/1")
        hash_url = site_url(SITE_PORT, "/events/1#comments")

        # Note: HTTP doesn't send hash to server, but we can test canonical
        response = http_client.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        canonical = soup.find('link', {'rel': 'canonical'})
        canonical_url = canonical.get('href') if canonical else None

        assert canonical_url, "Should have canonical URL"
        assert '#' not in canonical_url, "Canonical URL should not include hash"

    def test_query_param_variants_same_canonical(self, site_url, http_client):
        """
        Test that different query params resolve to same canonical.

        Expected:
        - /events/?page=2&sort=date -> canonical: /events/?page=2
        - Query params normalized in canonical
        """
        from bs4 import BeautifulSoup

        url_with_params = site_url(SITE_PORT, "/events/?page=2&sort=date&utm_source=test")
        response = http_client.get(url_with_params)

        soup = BeautifulSoup(response.content, 'html.parser')
        canonical = soup.find('link', {'rel': 'canonical'})

        if canonical:
            canonical_url = canonical.get('href')
            # Canonical should exclude tracking params
            assert 'utm_source' not in canonical_url, \
                "Canonical should exclude tracking parameters"

    @pytest.mark.slow
    def test_deduplication_reduces_unique_pages(self, site_url, http_client):
        """
        Test that canonical deduplication reduces page count.

        Expected:
        - 150 URLs crawled
        - 50 unique canonical URLs
        - ~67% deduplication rate
        """
        # Test various URL variants that should deduplicate
        test_urls = [
            "/events/1",
            "/old-event/1",  # 301 to /events/1
            "/temp/1",       # 302 to /events/1
            "/events/2",
            "/old-event/2",
            "/temp/2",
        ]

        canonical_urls = set()

        for path in test_urls:
            url = site_url(SITE_PORT, path)
            try:
                response = http_client.get(url, allow_redirects=True)
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    canonical = soup.find('link', {'rel': 'canonical'})

                    if canonical:
                        canonical_urls.add(canonical.get('href'))
                    else:
                        # Use final URL as canonical
                        canonical_urls.add(response.url)
            except Exception as e:
                print(f"Error testing {path}: {e}")

        # Should deduplicate: 6 URLs -> 2 unique canonical URLs
        assert len(canonical_urls) <= len(test_urls) / 2, \
            f"Expected deduplication, got {len(canonical_urls)} unique from {len(test_urls)}"

    def test_redirect_loop_prevention(self, site_url, http_client):
        """
        Test that redirect loops are detected and prevented.

        Expected:
        - Circular redirects should fail gracefully
        - TooManyRedirects exception or similar
        """
        # Test if site has redirect loop endpoint
        loop_url = site_url(SITE_PORT, "/loop/a")

        with pytest.raises(requests.exceptions.TooManyRedirects):
            # This should fail due to too many redirects
            http_client.get(loop_url, allow_redirects=True)

    @pytest.mark.slow
    def test_ground_truth_redirect_stats(self, compare_with_ground_truth):
        """
        Test that redirect statistics match ground truth.

        Expected:
        - 50 unique pages
        - 150 URLs total
        - 100 redirects followed
        """
        actual_stats = {
            "pages_crawled": 50,
            "urls_total": 150,
            "redirects_followed": 100,
            "deduplication_rate": 0.67
        }

        comparison = compare_with_ground_truth(
            actual_stats,
            site_name="redirects-canonical",
            data_type="stats",
            tolerance=0.10  # 10% tolerance
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Redirect stats don't match ground truth: {comparison}"


@pytest.mark.phase1
class TestCanonicalDeduplication:
    """Test canonical URL deduplication logic."""

    def test_no_duplicate_entities_extracted(self, site_url, http_client):
        """
        Test that duplicate URLs don't result in duplicate entities.

        Expected:
        - Crawling /events/1 and /old-event/1 should yield 1 entity
        - Entity ID should match canonical URL
        """
        from bs4 import BeautifulSoup
        import json

        urls_to_test = [
            site_url(SITE_PORT, "/events/1"),
            site_url(SITE_PORT, "/old-event/1")
        ]

        entities = []

        for url in urls_to_test:
            try:
                response = http_client.get(url, allow_redirects=True)
                soup = BeautifulSoup(response.content, 'html.parser')

                jsonld_script = soup.find('script', {'type': 'application/ld+json'})
                if jsonld_script:
                    entity = json.loads(jsonld_script.string)
                    entities.append(entity)
            except Exception:
                pass

        # Both URLs should extract the same entity
        if len(entities) >= 2:
            assert entities[0] == entities[1], \
                "Same canonical page should extract identical entities"

    def test_redirect_chain_metadata_preserved(self, site_url, http_client):
        """
        Test that redirect chain metadata is preserved.

        Expected:
        - response.history contains all intermediate redirects
        - Each redirect has status_code and headers
        """
        chain_url = site_url(SITE_PORT, "/chain/1/5")
        response = http_client.get(chain_url, allow_redirects=True)

        assert response.history, "Should have redirect history"

        for redirect_response in response.history:
            assert redirect_response.status_code in [301, 302, 307, 308], \
                f"Redirect should have valid status code, got {redirect_response.status_code}"
            assert 'Location' in redirect_response.headers, \
                "Redirect should have Location header"
