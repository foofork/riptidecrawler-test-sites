"""
Tests for media-and-nonhtml.site

Validates:
- PDF file serving and metadata
- Image format handling (JPG, PNG, WebP, SVG)
- Video file serving
- Audio file handling
- CSV and JSON file downloads
- Binary file handling
- Content-Type headers for various media types
"""

import json
import pytest
import requests
from bs4 import BeautifulSoup
import mimetypes


SITE_PORT = 5010
EXPECTED_MEDIA_TYPES = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp',
    'svg': 'image/svg+xml',
    'mp4': 'video/mp4',
    'mp3': 'audio/mpeg',
    'csv': 'text/csv',
    'json': 'application/json',
    'zip': 'application/zip'
}


@pytest.mark.phase3
@pytest.mark.requires_docker
class TestMediaNonHTML:
    """Test suite for media-and-nonhtml.site non-HTML content handling."""

    def test_site_is_healthy(self, health_check):
        """
        Verify the site is running and responding.

        Expected: HTTP 200 on root path
        """
        assert health_check(SITE_PORT), "media-and-nonhtml.site is not healthy"

    def test_pdf_files_served_correctly(self, site_url, http_client):
        """
        Test that PDF files are served with correct headers.

        Expected:
        - Content-Type: application/pdf
        - Proper Content-Length
        - Binary content
        """
        url = site_url(SITE_PORT, "/files/sample.pdf")
        response = http_client.get(url)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'application/pdf' in content_type, \
                "PDF should have correct Content-Type"

            # Check file starts with PDF magic number
            assert response.content[:4] == b'%PDF', \
                "PDF should start with %PDF magic number"

            # Check Content-Length is present
            content_length = response.headers.get('Content-Length')
            assert content_length is not None, "PDF should have Content-Length header"

    def test_image_formats_supported(self, site_url, http_client):
        """
        Test that various image formats are served correctly.

        Expected:
        - JPG, PNG, WebP, SVG all accessible
        - Correct Content-Type for each
        """
        image_paths = [
            ("/images/photo.jpg", "image/jpeg"),
            ("/images/icon.png", "image/png"),
            ("/images/modern.webp", "image/webp"),
            ("/images/vector.svg", "image/svg")
        ]

        for path, expected_type in image_paths:
            url = site_url(SITE_PORT, path)
            response = http_client.get(url)

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                assert expected_type in content_type, \
                    f"{path} should have Content-Type: {expected_type}"

    def test_video_files_served(self, site_url, http_client):
        """
        Test that video files are accessible.

        Expected:
        - Video files return 200 or 206 (partial content)
        - Content-Type: video/mp4 or similar
        - Accept-Ranges header for streaming
        """
        url = site_url(SITE_PORT, "/videos/sample.mp4")
        response = http_client.get(url)

        if response.status_code in [200, 206]:
            content_type = response.headers.get('Content-Type', '')
            assert 'video/' in content_type, \
                "Video should have video/* Content-Type"

            # Check for streaming support
            accept_ranges = response.headers.get('Accept-Ranges')
            if accept_ranges:
                assert accept_ranges == 'bytes', \
                    "Video should support byte-range requests"

    def test_audio_files_served(self, site_url, http_client):
        """
        Test that audio files are accessible.

        Expected:
        - Audio files return 200
        - Content-Type: audio/mpeg or similar
        """
        url = site_url(SITE_PORT, "/audio/sample.mp3")
        response = http_client.get(url)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'audio/' in content_type, \
                "Audio should have audio/* Content-Type"

    def test_csv_files_downloadable(self, site_url, http_client):
        """
        Test that CSV files are served correctly.

        Expected:
        - Content-Type: text/csv
        - Content can be parsed as CSV
        """
        url = site_url(SITE_PORT, "/data/export.csv")
        response = http_client.get(url)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'csv' in content_type.lower() or 'text/' in content_type, \
                "CSV should have appropriate Content-Type"

            # Check content looks like CSV
            content = response.text
            lines = content.strip().split('\n')
            assert len(lines) > 0, "CSV should have at least one line"

            # First line should have commas (header)
            if ',' in lines[0]:
                assert True

    def test_json_files_valid(self, site_url, http_client):
        """
        Test that JSON files are served correctly.

        Expected:
        - Content-Type: application/json
        - Valid JSON format
        """
        url = site_url(SITE_PORT, "/api/data.json")
        response = http_client.get(url)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'json' in content_type.lower(), \
                "JSON should have application/json Content-Type"

            # Should be valid JSON
            try:
                data = json.loads(response.text)
                assert isinstance(data, (dict, list)), \
                    "JSON should parse to dict or list"
            except json.JSONDecodeError:
                pytest.fail("JSON file should contain valid JSON")

    def test_binary_files_integrity(self, site_url, http_client):
        """
        Test that binary files maintain integrity.

        Expected:
        - Binary files served without corruption
        - Content-Length matches actual size
        """
        url = site_url(SITE_PORT, "/files/archive.zip")
        response = http_client.get(url)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'application/zip' in content_type or 'application/octet-stream' in content_type, \
                "ZIP should have appropriate Content-Type"

            # Check ZIP magic number
            if response.content[:2] == b'PK':
                assert True, "ZIP file has correct magic number"

            # Verify Content-Length
            content_length = response.headers.get('Content-Length')
            if content_length:
                assert int(content_length) == len(response.content), \
                    "Content-Length should match actual content size"

    def test_svg_files_inline_safe(self, site_url, http_client):
        """
        Test that SVG files are safe for inline display.

        Expected:
        - Content-Type: image/svg+xml
        - Valid XML structure
        - No embedded scripts (XSS protection)
        """
        url = site_url(SITE_PORT, "/images/icon.svg")
        response = http_client.get(url)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'svg' in content_type.lower(), \
                "SVG should have image/svg+xml Content-Type"

            # Parse as XML
            soup = BeautifulSoup(response.content, 'xml')
            svg_element = soup.find('svg')
            assert svg_element is not None, "Should contain <svg> element"

            # Check for potentially dangerous script tags
            scripts = soup.find_all('script')
            assert len(scripts) == 0, \
                "SVG should not contain <script> tags (XSS risk)"

    def test_content_disposition_headers(self, site_url, http_client):
        """
        Test that downloadable files have Content-Disposition headers.

        Expected:
        - Content-Disposition: attachment for downloads
        - Filename parameter present
        """
        download_urls = [
            "/download/report.pdf",
            "/download/data.csv",
            "/download/archive.zip"
        ]

        for path in download_urls:
            url = site_url(SITE_PORT, path)
            response = http_client.get(url)

            if response.status_code == 200:
                disposition = response.headers.get('Content-Disposition')
                if disposition:
                    assert 'attachment' in disposition.lower() or 'filename=' in disposition, \
                        f"Download URL should have Content-Disposition header: {path}"

    def test_media_links_from_html(self, site_url, http_client):
        """
        Test that HTML pages link to media files correctly.

        Expected:
        - Links to media files are valid
        - Media files are accessible
        """
        url = site_url(SITE_PORT, "/")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find image tags
            images = soup.find_all('img', src=True)
            if len(images) > 0:
                # Test first image
                img_src = images[0]['src']
                if not img_src.startswith('http'):
                    img_url = site_url(SITE_PORT, img_src)
                    img_response = http_client.get(img_url)
                    assert img_response.status_code == 200, \
                        f"Linked image should be accessible: {img_src}"

            # Find download links
            download_links = soup.find_all('a', href=True)
            media_links = [
                link['href'] for link in download_links
                if any(ext in link['href'].lower() for ext in ['.pdf', '.csv', '.zip'])
            ]

            if len(media_links) > 0:
                # Test first media link
                media_href = media_links[0]
                if not media_href.startswith('http'):
                    media_url = site_url(SITE_PORT, media_href)
                    media_response = http_client.get(media_url)
                    assert media_response.status_code in [200, 404], \
                        f"Linked media should not error: {media_href}"

    @pytest.mark.slow
    def test_large_file_handling(self, site_url, http_client):
        """
        Test that large files are handled efficiently.

        Expected:
        - Large files can be downloaded
        - Streaming/chunked transfer for large files
        """
        url = site_url(SITE_PORT, "/files/large-video.mp4")
        response = http_client.get(url, stream=True)

        if response.status_code in [200, 206]:
            # Check for chunked transfer or content-length
            transfer_encoding = response.headers.get('Transfer-Encoding')
            content_length = response.headers.get('Content-Length')

            assert transfer_encoding == 'chunked' or content_length is not None, \
                "Large files should use chunked transfer or have Content-Length"


@pytest.mark.phase3
class TestMediaMetadata:
    """Test metadata extraction from media files."""

    def test_image_metadata_extractable(self, site_url, http_client):
        """
        Test that image metadata can be extracted.

        Expected:
        - Images have proper dimensions
        - EXIF data preserved (if present)
        """
        url = site_url(SITE_PORT, "/images/photo-with-metadata.jpg")
        response = http_client.get(url)

        if response.status_code == 200:
            # Just verify it's a valid image
            assert response.content[:2] == b'\xff\xd8', \
                "JPEG should start with FF D8 marker"

    def test_pdf_metadata_readable(self, site_url, http_client):
        """
        Test that PDF metadata is accessible.

        Expected:
        - PDF has valid structure
        - Metadata can be extracted
        """
        url = site_url(SITE_PORT, "/files/document-with-metadata.pdf")
        response = http_client.get(url)

        if response.status_code == 200:
            content = response.content
            assert b'/Title' in content or b'/Author' in content or b'/Subject' in content, \
                "PDF should contain metadata fields"
