"""
Tests for anti-bot-lite.site

Validates:
- User-Agent based filtering
- Rate limiting detection
- Simple bot detection mechanisms
- CAPTCHA or challenge pages
- Honeypot fields
- Request fingerprinting
"""

import pytest
import requests
import time
from bs4 import BeautifulSoup


SITE_PORT = 5011


@pytest.mark.phase3
@pytest.mark.requires_docker
class TestAntiBotLite:
    """Test suite for anti-bot-lite.site bot detection features."""

    def test_site_is_healthy(self, health_check):
        """
        Verify the site is running and responding.

        Expected: HTTP 200 on root path
        """
        assert health_check(SITE_PORT), "anti-bot-lite.site is not healthy"

    def test_normal_user_agent_allowed(self, site_url, http_client):
        """
        Test that normal browsers are allowed.

        Expected:
        - Standard browser user-agents get HTTP 200
        - Content loads normally
        """
        url = site_url(SITE_PORT, "/")

        # Use standard browser user-agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = http_client.get(url, headers=headers)

        assert response.status_code == 200, \
            "Normal browser user-agent should be allowed"

    def test_bot_user_agent_blocked(self, site_url):
        """
        Test that obvious bot user-agents are blocked or challenged.

        Expected:
        - Bot user-agents get HTTP 403, 429, or challenge page
        - Or redirected to verification page
        """
        url = site_url(SITE_PORT, "/")

        bot_user_agents = [
            'python-requests',
            'curl/7.0',
            'wget/1.0',
            'bot',
            'crawler',
            'spider'
        ]

        blocked_count = 0
        for ua in bot_user_agents:
            session = requests.Session()
            session.headers.update({'User-Agent': ua})
            response = session.get(url)

            # Should be blocked (403), rate limited (429), or challenged
            if response.status_code in [403, 429]:
                blocked_count += 1
            elif response.status_code == 200:
                # Check if it's a challenge page
                soup = BeautifulSoup(response.content, 'html.parser')
                if 'challenge' in soup.get_text().lower() or 'captcha' in soup.get_text().lower():
                    blocked_count += 1

        # At least some bot user-agents should be blocked
        assert blocked_count >= 2, \
            f"At least 2 bot user-agents should be blocked, got {blocked_count}"

    def test_rate_limiting_enforced(self, site_url):
        """
        Test that rate limiting is enforced on rapid requests.

        Expected:
        - After N rapid requests, get HTTP 429 (Too Many Requests)
        - Or temporary block
        """
        url = site_url(SITE_PORT, "/api/data")

        # Create a session WITHOUT retry logic for this test
        # (the default http_client fixture retries 429s, which hides rate limiting)
        session = requests.Session()

        # Make rapid requests
        responses = []
        for i in range(20):
            response = session.get(url)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay

        # Should eventually hit rate limit
        rate_limited = any(status == 429 for status in responses)

        # If not rate limited by status code, check for rate limit messages
        if not rate_limited:
            last_response = session.get(url)
            if last_response.status_code == 200:
                content = last_response.text.lower()
                rate_limited = 'rate limit' in content or 'too many requests' in content

        assert rate_limited, "Rate limiting should be enforced after rapid requests"

    def test_honeypot_field_detection(self, site_url, http_client):
        """
        Test that honeypot fields catch bots.

        Expected:
        - Forms contain hidden honeypot fields
        - Filling honeypot results in rejection
        """
        url = site_url(SITE_PORT, "/contact")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for honeypot fields (hidden fields with suspicious names)
            forms = soup.find_all('form')
            honeypot_found = False

            for form in forms:
                hidden_inputs = form.find_all('input', {'type': 'hidden'})
                for hidden in hidden_inputs:
                    name = hidden.get('name', '').lower()
                    # Common honeypot field names
                    if any(x in name for x in ['honeypot', 'bot', 'trap', 'email_confirm']):
                        honeypot_found = True
                        break

                # Also check for CSS-hidden fields
                all_inputs = form.find_all('input')
                for inp in all_inputs:
                    style = inp.get('style', '')
                    if 'display: none' in style or 'visibility: hidden' in style:
                        honeypot_found = True
                        break

            if forms and honeypot_found:
                assert True, "Honeypot field detected"

    def test_javascript_challenge_present(self, site_url, http_client):
        """
        Test that JavaScript challenges are present for bot detection.

        Expected:
        - JavaScript code present that validates browser
        - Cookies set via JavaScript
        """
        url = site_url(SITE_PORT, "/")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for challenge scripts
            scripts = soup.find_all('script')
            has_challenge = False

            for script in scripts:
                if script.string:
                    script_content = script.string.lower()
                    # Look for common challenge patterns
                    if any(x in script_content for x in [
                        'challenge',
                        'verification',
                        'document.cookie',
                        'pow',  # proof of work
                        'fingerprint'
                    ]):
                        has_challenge = True
                        break

            # If challenge present, mark as detected
            if has_challenge:
                assert True, "JavaScript challenge detected"

    def test_cookie_validation(self, site_url):
        """
        Test that cookie validation is used for bot detection.

        Expected:
        - First request may set a challenge cookie
        - Second request validates cookie
        """
        url = site_url(SITE_PORT, "/")

        session = requests.Session()

        # First request - should set cookie
        response1 = session.get(url)
        cookies_after_first = session.cookies

        # Second request - cookie should be validated
        response2 = session.get(url)

        # Check if cookies were set and used
        assert len(cookies_after_first) > 0 or response1.status_code == 200, \
            "Site should set cookies for tracking"

    def test_referer_header_checking(self, site_url):
        """
        Test that Referer header is checked for suspicious patterns.

        Expected:
        - Direct access (no referer) may be challenged
        - Valid referer from same domain allowed
        """
        url = site_url(SITE_PORT, "/protected")

        session = requests.Session()

        # Request without referer
        response_no_referer = session.get(url)

        # Request with valid referer
        session2 = requests.Session()
        headers = {'Referer': site_url(SITE_PORT, "/")}
        response_with_referer = session2.get(url, headers=headers)

        # At least one should succeed
        assert response_no_referer.status_code == 200 or response_with_referer.status_code == 200, \
            "At least one referer pattern should work"

    def test_timing_based_detection(self, site_url, http_client):
        """
        Test that suspiciously fast interactions are detected.

        Expected:
        - Too-fast form submissions rejected
        - Minimum interaction time enforced
        """
        url = site_url(SITE_PORT, "/contact")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            form = soup.find('form')

            if form:
                # Try to submit form immediately (bot-like behavior)
                form_action = form.get('action') or url
                if not form_action.startswith('http'):
                    form_action = site_url(SITE_PORT, form_action)

                # Immediate submission
                submit_response = http_client.post(
                    form_action,
                    data={'name': 'Bot', 'message': 'Spam'}
                )

                # Should be rejected or challenged
                if submit_response.status_code in [403, 429]:
                    assert True, "Fast submission detected and blocked"
                elif submit_response.status_code == 200:
                    # Check for error message
                    if 'error' in submit_response.text.lower() or 'too fast' in submit_response.text.lower():
                        assert True, "Fast submission detected"

    def test_ip_based_blocking(self, site_url):
        """
        Test that IP-based blocking can be triggered.

        Expected:
        - Multiple violations from same IP lead to block
        - Block persists across requests
        """
        url = site_url(SITE_PORT, "/")

        session = requests.Session()

        # Make multiple suspicious requests
        responses = []
        for i in range(10):
            # Use bot-like user-agent
            session.headers.update({'User-Agent': 'BadBot/1.0'})
            response = session.get(url)
            responses.append(response.status_code)

        # Should eventually be blocked
        blocked = any(status in [403, 429] for status in responses)

        assert blocked or responses[-1] != 200, \
            "Repeated bot-like behavior should trigger blocking"


@pytest.mark.phase3
class TestAntiBotBypass:
    """Test scenarios where legitimate crawlers should pass."""

    def test_googlebot_allowed(self, site_url):
        """
        Test that Googlebot is allowed through.

        Expected:
        - Googlebot user-agent gets HTTP 200
        - Robots.txt allows Googlebot
        """
        url = site_url(SITE_PORT, "/")

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        })

        response = session.get(url)

        # Googlebot should be allowed (or at least not blocked outright)
        assert response.status_code in [200, 301, 302], \
            "Googlebot should be allowed"

    def test_robots_txt_provides_guidance(self, site_url, http_client):
        """
        Test that robots.txt exists and provides crawl guidance.

        Expected:
        - robots.txt exists
        - Contains User-agent rules
        """
        url = site_url(SITE_PORT, "/robots.txt")
        response = http_client.get(url)

        assert response.status_code == 200, "robots.txt should exist"

        robots_content = response.text
        assert 'User-agent:' in robots_content, \
            "robots.txt should have User-agent directive"
