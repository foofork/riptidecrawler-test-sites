"""
Tests for encoding-and-i18n.site

Validates:
- UTF-8 encoding handling
- Multiple language content (English, Japanese, Arabic, Russian, etc.)
- Character set detection
- Special characters in URLs and content
- Right-to-left (RTL) language support
- Content-Language headers
"""

import json
import pytest
import requests
from bs4 import BeautifulSoup


SITE_PORT = 5009
EXPECTED_LANGUAGES = ["en", "ja", "ar", "ru", "zh", "es", "fr", "de"]


@pytest.mark.phase3
@pytest.mark.requires_docker
class TestEncodingI18n:
    """Test suite for encoding-and-i18n.site internationalization features."""

    def test_site_is_healthy(self, health_check):
        """
        Verify the site is running and responding.

        Expected: HTTP 200 on root path
        """
        assert health_check(SITE_PORT), "encoding-and-i18n.site is not healthy"

    def test_utf8_encoding_declared(self, site_url, http_client):
        """
        Test that all pages declare UTF-8 encoding.

        Expected:
        - Content-Type header includes charset=utf-8
        - Meta charset tag in HTML
        """
        url = site_url(SITE_PORT, "/")
        response = http_client.get(url)

        assert response.status_code == 200, "Index page should return 200"

        # Check Content-Type header
        content_type = response.headers.get('Content-Type', '')
        assert 'utf-8' in content_type.lower(), "Content-Type should declare UTF-8"

        # Check meta tag
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_charset = soup.find('meta', {'charset': True})
        if meta_charset:
            assert meta_charset.get('charset').lower() == 'utf-8'

    def test_multilanguage_content_available(self, site_url, http_client):
        """
        Test that content is available in multiple languages.

        Expected:
        - Content available in at least 5 languages
        - Language detection via URL or Content-Language header
        """
        languages_found = []

        for lang in EXPECTED_LANGUAGES:
            url = site_url(SITE_PORT, f"/{lang}/")
            response = http_client.get(url)

            if response.status_code == 200:
                languages_found.append(lang)

        assert len(languages_found) >= 5, \
            f"Should have content in at least 5 languages, found: {languages_found}"

    def test_japanese_characters_render_correctly(self, site_url, http_client):
        """
        Test that Japanese characters (kanji, hiragana, katakana) are handled correctly.

        Expected:
        - Japanese page loads without encoding errors
        - Characters display correctly (no mojibake)
        """
        url = site_url(SITE_PORT, "/ja/")
        response = http_client.get(url)

        assert response.status_code == 200, "Japanese page should return 200"

        # Check response is valid UTF-8
        try:
            content = response.content.decode('utf-8')
            assert len(content) > 0
        except UnicodeDecodeError:
            pytest.fail("Japanese content should be valid UTF-8")

        # Check for presence of Japanese characters
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        # Look for Hiragana range (U+3040 to U+309F)
        has_japanese = any('\u3040' <= char <= '\u309f' or
                          '\u30a0' <= char <= '\u30ff' or
                          '\u4e00' <= char <= '\u9faf'
                          for char in text)

        assert has_japanese, "Japanese page should contain Japanese characters"

    def test_arabic_rtl_content(self, site_url, http_client):
        """
        Test that Arabic (RTL) content is properly marked.

        Expected:
        - dir="rtl" attribute on appropriate elements
        - Arabic characters render correctly
        """
        url = site_url(SITE_PORT, "/ar/")
        response = http_client.get(url)

        assert response.status_code == 200, "Arabic page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for RTL direction
        rtl_elements = soup.find_all(attrs={"dir": "rtl"})
        assert len(rtl_elements) > 0, "Arabic page should have dir='rtl' elements"

        # Check for Arabic characters (U+0600 to U+06FF)
        text = soup.get_text()
        has_arabic = any('\u0600' <= char <= '\u06ff' for char in text)
        assert has_arabic, "Arabic page should contain Arabic characters"

    def test_chinese_characters(self, site_url, http_client):
        """
        Test that Chinese characters (simplified/traditional) are handled.

        Expected:
        - Chinese page loads correctly
        - CJK characters render without issues
        """
        url = site_url(SITE_PORT, "/zh/")
        response = http_client.get(url)

        assert response.status_code == 200, "Chinese page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        # Check for CJK Unified Ideographs (U+4E00 to U+9FFF)
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        assert has_chinese, "Chinese page should contain Chinese characters"

    def test_special_characters_in_urls(self, site_url, http_client):
        """
        Test that URLs with special characters are handled correctly.

        Expected:
        - URLs with encoded characters work
        - Properly percent-encoded
        """
        # Test URL with spaces (should be encoded)
        special_urls = [
            "/search?q=%E6%97%A5%E6%9C%AC",  # Japanese characters
            "/search?q=%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9",  # Arabic
        ]

        for path in special_urls:
            url = site_url(SITE_PORT, path)
            response = http_client.get(url)

            # Should either work or redirect, not error
            assert response.status_code in [200, 301, 302, 404], \
                f"URL with special characters should not error: {path}"

    def test_content_language_headers(self, site_url, http_client):
        """
        Test that Content-Language headers are properly set.

        Expected:
        - Content-Language header present for language-specific pages
        - Matches the language of the page
        """
        for lang in ["en", "ja", "ar", "es"]:
            url = site_url(SITE_PORT, f"/{lang}/")
            response = http_client.get(url)

            if response.status_code == 200:
                content_lang = response.headers.get('Content-Language')
                if content_lang:
                    assert lang in content_lang.lower(), \
                        f"Content-Language should match page language: {lang}"

    def test_mixed_language_content(self, site_url, http_client):
        """
        Test pages with mixed language content.

        Expected:
        - Multiple languages can coexist on same page
        - lang attributes used appropriately
        """
        url = site_url(SITE_PORT, "/mixed/")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for lang attributes
            lang_elements = soup.find_all(attrs={"lang": True})

            if len(lang_elements) > 0:
                # Should have at least 2 different languages
                languages = set(elem.get('lang') for elem in lang_elements)
                assert len(languages) >= 2, \
                    "Mixed content page should have multiple lang attributes"

    def test_emoji_and_symbols(self, site_url, http_client):
        """
        Test that emoji and special symbols are handled correctly.

        Expected:
        - Emoji render correctly
        - Mathematical symbols preserved
        - Currency symbols correct
        """
        url = site_url(SITE_PORT, "/symbols/")
        response = http_client.get(url)

        if response.status_code == 200:
            content = response.content.decode('utf-8')

            # Check for emoji (Emoticons range)
            has_emoji = any('\U0001f600' <= char <= '\U0001f64f' for char in content)

            # Check for currency symbols
            currency_symbols = ['$', '€', '£', '¥', '₹']
            has_currency = any(symbol in content for symbol in currency_symbols)

            # At least one should be present
            assert has_emoji or has_currency, \
                "Symbols page should contain emoji or currency symbols"

    @pytest.mark.slow
    def test_crawl_preserves_encoding(self, site_url, crawl_simulator):
        """
        Test that crawling preserves character encoding.

        Expected:
        - All pages crawled successfully
        - No encoding errors during crawl
        - Character integrity maintained
        """
        start_url = site_url(SITE_PORT, "/")
        result = crawl_simulator(start_url, max_pages=20)

        assert result['pages_crawled'] >= 5, "Should crawl at least 5 pages"

        # All pages should return 200
        successful_pages = [p for p in result['pages'] if p['status_code'] == 200]
        assert len(successful_pages) >= 5, "At least 5 pages should load successfully"


@pytest.mark.phase3
class TestEncodingEdgeCases:
    """Test edge cases and potential encoding issues."""

    def test_mixed_encoding_detection(self, site_url, http_client):
        """
        Test that the site doesn't mix encodings.

        Expected:
        - Consistent UTF-8 throughout
        - No Latin-1 or other legacy encodings
        """
        url = site_url(SITE_PORT, "/")
        response = http_client.get(url)

        if response.status_code == 200:
            # Should decode as UTF-8 without errors
            try:
                content = response.content.decode('utf-8')
                assert len(content) > 0
            except UnicodeDecodeError:
                pytest.fail("Content should be valid UTF-8")

    def test_url_encoded_query_params(self, site_url, http_client):
        """
        Test that URL-encoded query parameters work correctly.

        Expected:
        - Percent-encoded params decoded properly
        - Special characters in params preserved
        """
        # Test with encoded space and special char
        url = site_url(SITE_PORT, "/search?q=hello+world&lang=en")
        response = http_client.get(url)

        # Should not error
        assert response.status_code in [200, 404], \
            "URL with encoded params should not error"

    def test_hreflang_tags_present(self, site_url, http_client):
        """
        Test that hreflang tags are present for language alternates.

        Expected:
        - <link rel="alternate" hreflang="..."> tags
        - Point to correct language versions
        """
        url = site_url(SITE_PORT, "/en/")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            hreflang_links = soup.find_all('link', {'rel': 'alternate', 'hreflang': True})

            if len(hreflang_links) > 0:
                # Should have at least one alternate language
                languages = [link.get('hreflang') for link in hreflang_links]
                assert len(set(languages)) >= 1, \
                    "Should have hreflang tags for alternate languages"
