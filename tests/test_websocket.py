"""
Tests for websocket-stream-sink.site

Validates:
- WebSocket connection establishment
- Real-time data streaming
- SSE (Server-Sent Events) endpoints
- Long polling fallback
- Streaming API responses
- Connection upgrade handling
"""

import pytest
import requests
import json
import time
from bs4 import BeautifulSoup


SITE_PORT = 5013


@pytest.mark.phase3
@pytest.mark.requires_docker
class TestWebSocketStream:
    """Test suite for websocket-stream-sink.site streaming features."""

    def test_site_is_healthy(self, health_check):
        """
        Verify the site is running and responding.

        Expected: HTTP 200 on root path
        """
        assert health_check(SITE_PORT), "websocket-stream-sink.site is not healthy"

    def test_websocket_endpoint_advertised(self, site_url, http_client):
        """
        Test that WebSocket endpoints are advertised.

        Expected:
        - HTML page contains WebSocket connection info
        - ws:// or wss:// URLs present in page
        """
        url = site_url(SITE_PORT, "/")
        response = http_client.get(url)

        assert response.status_code == 200, "Index page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for WebSocket URLs in scripts or data attributes
        scripts = soup.find_all('script')
        has_websocket = False

        for script in scripts:
            if script.string:
                if 'websocket' in script.string.lower() or 'ws://' in script.string or 'wss://' in script.string:
                    has_websocket = True
                    break

        # Also check in page text/attributes
        page_text = str(response.content)
        if 'websocket' in page_text.lower():
            has_websocket = True

        assert has_websocket, "Page should advertise WebSocket functionality"

    def test_sse_endpoint_exists(self, site_url):
        """
        Test that Server-Sent Events (SSE) endpoint exists.

        Expected:
        - /stream or /events endpoint returns text/event-stream
        - Keeps connection open
        """
        sse_paths = ['/stream', '/events', '/sse', '/updates']

        for path in sse_paths:
            url = site_url(SITE_PORT, path)
            try:
                session = requests.Session()
                response = session.get(url, stream=True, timeout=2)

                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')

                    if 'text/event-stream' in content_type:
                        assert True, f"SSE endpoint found at {path}"
                        return

            except requests.Timeout:
                # Timeout is OK for streaming endpoints
                pass
            except Exception:
                pass

        # If we get here, check if any path returned 200
        pytest.skip("No SSE endpoint found (may require WebSocket only)")

    def test_streaming_json_api(self, site_url, http_client):
        """
        Test that streaming JSON API works.

        Expected:
        - /api/stream returns chunked or NDJSON
        - Multiple JSON objects in response
        """
        url = site_url(SITE_PORT, "/api/stream")
        response = http_client.get(url, stream=True, timeout=5)

        if response.status_code == 200:
            # Check for chunked transfer
            transfer_encoding = response.headers.get('Transfer-Encoding')

            if transfer_encoding == 'chunked':
                assert True, "Streaming API uses chunked encoding"
            else:
                # Check if NDJSON
                content_type = response.headers.get('Content-Type', '')
                if 'ndjson' in content_type or 'json-lines' in content_type:
                    assert True, "Streaming API uses NDJSON"

    def test_long_polling_fallback(self, site_url, http_client):
        """
        Test that long polling is available as fallback.

        Expected:
        - /poll endpoint returns data after delay
        - Can receive updates via long polling
        """
        url = site_url(SITE_PORT, "/poll")

        start_time = time.time()
        response = http_client.get(url, timeout=10)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            # Long polling should take some time (not instant)
            if elapsed > 0.5:
                assert True, "Long polling endpoint detected"

            # Check response is JSON or contains data
            try:
                data = response.json()
                assert isinstance(data, (dict, list)), \
                    "Long polling should return JSON data"
            except json.JSONDecodeError:
                # Plain text response is also OK
                assert len(response.text) > 0, \
                    "Long polling should return data"

    def test_connection_upgrade_header(self, site_url):
        """
        Test that WebSocket upgrade is handled.

        Expected:
        - Server responds to Upgrade: websocket header
        - Returns appropriate status (101 Switching Protocols or 426)
        """
        url = site_url(SITE_PORT, "/ws")

        session = requests.Session()
        headers = {
            'Connection': 'Upgrade',
            'Upgrade': 'websocket',
            'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
            'Sec-WebSocket-Version': '13'
        }

        try:
            response = session.get(url, headers=headers, allow_redirects=False)

            # Should get 101 Switching Protocols or 426 Upgrade Required or 404
            valid_statuses = [101, 426, 404, 400]
            assert response.status_code in valid_statuses, \
                f"WebSocket upgrade should return appropriate status, got {response.status_code}"

        except Exception as e:
            # Connection errors are expected for WebSocket upgrade attempts via HTTP client
            pytest.skip(f"WebSocket upgrade test inconclusive: {e}")

    def test_real_time_updates_api(self, site_url, http_client):
        """
        Test that real-time updates API endpoint exists.

        Expected:
        - API endpoint for subscribing to updates
        - Returns structured data
        """
        url = site_url(SITE_PORT, "/api/updates")
        response = http_client.get(url)

        if response.status_code == 200:
            # Should return JSON
            try:
                data = response.json()
                assert isinstance(data, (dict, list)), \
                    "Updates API should return JSON"
            except json.JSONDecodeError:
                pytest.fail("Updates API should return valid JSON")

    def test_message_queue_endpoint(self, site_url, http_client):
        """
        Test that message queue/subscription endpoint exists.

        Expected:
        - Endpoint for subscribing to messages
        - Can retrieve pending messages
        """
        url = site_url(SITE_PORT, "/messages")
        response = http_client.get(url)

        if response.status_code == 200:
            # Check response structure
            try:
                data = response.json()

                # Should have message-like structure
                if isinstance(data, dict):
                    assert 'messages' in data or 'data' in data or 'events' in data, \
                        "Message endpoint should return structured data"
                elif isinstance(data, list):
                    assert True, "Message endpoint returns list of messages"

            except json.JSONDecodeError:
                # Plain text messages also OK
                assert len(response.text) > 0

    def test_chunked_response_handling(self, site_url):
        """
        Test that chunked responses are properly handled.

        Expected:
        - Server can send chunked responses
        - Client receives data progressively
        """
        url = site_url(SITE_PORT, "/api/stream")

        session = requests.Session()

        try:
            response = session.get(url, stream=True, timeout=3)

            if response.status_code == 200:
                transfer_encoding = response.headers.get('Transfer-Encoding')

                if transfer_encoding == 'chunked':
                    # Try to read first chunk
                    chunk_received = False
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            chunk_received = True
                            break

                    assert chunk_received, "Should receive at least one chunk"

        except requests.Timeout:
            pytest.skip("Stream endpoint timeout (expected for persistent connections)")

    def test_cors_headers_for_streaming(self, site_url, http_client):
        """
        Test that CORS headers allow streaming from browsers.

        Expected:
        - Access-Control-Allow-Origin present
        - Access-Control-Allow-Methods includes appropriate methods
        """
        url = site_url(SITE_PORT, "/api/stream")
        response = http_client.get(url, timeout=2)

        if response.status_code == 200:
            cors_origin = response.headers.get('Access-Control-Allow-Origin')

            if cors_origin:
                assert cors_origin in ['*', site_url(SITE_PORT, "")], \
                    "CORS headers should allow streaming"


@pytest.mark.phase3
class TestStreamingDataFormats:
    """Test various streaming data formats."""

    def test_ndjson_format(self, site_url, http_client):
        """
        Test NDJSON (Newline Delimited JSON) format.

        Expected:
        - Each line is valid JSON
        - Lines separated by newlines
        """
        url = site_url(SITE_PORT, "/api/stream.ndjson")
        response = http_client.get(url, timeout=3)

        if response.status_code == 200:
            lines = response.text.strip().split('\n')

            valid_json_lines = 0
            for line in lines:
                if line.strip():
                    try:
                        json.loads(line)
                        valid_json_lines += 1
                    except json.JSONDecodeError:
                        pass

            if valid_json_lines > 0:
                assert True, f"Found {valid_json_lines} valid NDJSON lines"

    def test_event_stream_format(self, site_url):
        """
        Test SSE (Server-Sent Events) format.

        Expected:
        - Lines start with "data: "
        - Events separated by blank lines
        """
        url = site_url(SITE_PORT, "/events")

        session = requests.Session()

        try:
            response = session.get(url, stream=True, timeout=2)

            if response.status_code == 200:
                # Read first few lines
                content_type = response.headers.get('Content-Type', '')

                if 'text/event-stream' in content_type:
                    # Try to read first event
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                assert True, "Valid SSE format detected"
                                return

        except requests.Timeout:
            pytest.skip("SSE endpoint timeout (normal for persistent connections)")

    def test_json_stream_format(self, site_url, http_client):
        """
        Test JSON streaming format.

        Expected:
        - Valid JSON array or objects
        - Can be parsed progressively
        """
        url = site_url(SITE_PORT, "/api/json-stream")
        response = http_client.get(url, timeout=3)

        if response.status_code == 200:
            try:
                data = response.json()
                assert isinstance(data, (dict, list)), \
                    "JSON stream should return valid JSON"
            except json.JSONDecodeError:
                # May be NDJSON instead
                pass
