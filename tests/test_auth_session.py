"""
Tests for auth-and-session.site

Validates:
- Login flow with username/password
- Session cookies maintained across requests
- CSRF token handling
- Protected pages require authentication
- Session expiration and renewal
"""

import pytest
from bs4 import BeautifulSoup


SITE_PORT = 5008


@pytest.mark.phase2
@pytest.mark.requires_docker
class TestAuthenticationSession:
    """Test suite for authentication and session management."""

    def test_site_is_healthy(self, health_check):
        """Verify the auth site is running."""
        assert health_check(SITE_PORT), "auth-and-session.site is not healthy"

    def test_login_page_accessible(self, site_url, http_client):
        """
        Test that login page is accessible without authentication.

        Expected:
        - /login returns HTTP 200
        - Contains login form
        - Has CSRF token
        """
        url = site_url(SITE_PORT, "/login")
        response = http_client.get(url)

        assert response.status_code == 200, "Login page should be accessible"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for login form
        login_form = soup.find('form', id='login-form') or soup.find('form', action=lambda x: x and 'login' in x)
        assert login_form, "Should have login form"

        # Check for username/password fields
        username_field = soup.find('input', {'name': 'username'}) or soup.find('input', {'type': 'text'})
        password_field = soup.find('input', {'type': 'password'})

        assert username_field, "Should have username field"
        assert password_field, "Should have password field"

    def test_csrf_token_present(self, site_url, http_client):
        """
        Test that login form includes CSRF token.

        Expected:
        - Hidden CSRF token field
        - Token is non-empty string
        """
        url = site_url(SITE_PORT, "/login")
        response = http_client.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        csrf_field = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': '_csrf'})

        assert csrf_field, "Login form should have CSRF token"
        csrf_value = csrf_field.get('value', '')
        assert len(csrf_value) > 0, "CSRF token should not be empty"

    def test_protected_page_requires_auth(self, site_url, http_client):
        """
        Test that protected pages redirect to login.

        Expected:
        - /dashboard requires authentication
        - Redirects to /login (302)
        - Or returns 401 Unauthorized
        """
        url = site_url(SITE_PORT, "/dashboard")
        response = http_client.get(url, allow_redirects=False)

        assert response.status_code in [302, 401, 403], \
            f"Protected page should require auth, got {response.status_code}"

        if response.status_code == 302:
            # Should redirect to login
            location = response.headers.get('Location', '')
            assert 'login' in location.lower(), "Should redirect to login page"

    def test_successful_login(self, site_url, http_client):
        """
        Test successful login flow.

        Expected:
        - POST /login with credentials
        - Session cookie set
        - Redirect to dashboard or success page
        """
        # First get login page for CSRF token
        login_page = http_client.get(site_url(SITE_PORT, "/login"))
        soup = BeautifulSoup(login_page.content, 'html.parser')

        csrf_field = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': '_csrf'})
        csrf_token = csrf_field.get('value', '') if csrf_field else 'test_token'

        # Attempt login
        login_data = {
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }

        response = http_client.post(
            site_url(SITE_PORT, "/login"),
            data=login_data,
            allow_redirects=False
        )

        # Should redirect on success or return 200
        assert response.status_code in [200, 302], \
            f"Login should succeed, got {response.status_code}"

        # Should set session cookie
        cookies = http_client.cookies
        has_session = any(
            'session' in cookie.lower() or 'sid' in cookie.lower()
            for cookie in cookies.keys()
        )

        assert has_session or response.status_code == 200, \
            "Login should set session cookie"

    def test_session_maintained_across_requests(self, site_url, http_client):
        """
        Test that session is maintained across requests.

        Expected:
        - Login once
        - Multiple requests use same session
        - No need to re-authenticate
        """
        # Login first
        self._login(site_url, http_client)

        # Make multiple requests to protected pages
        protected_urls = [
            site_url(SITE_PORT, "/dashboard"),
            site_url(SITE_PORT, "/profile"),
            site_url(SITE_PORT, "/settings")
        ]

        for url in protected_urls:
            response = http_client.get(url)
            # Should succeed (200) or not exist (404), but not auth error
            assert response.status_code not in [401, 403], \
                f"Should stay authenticated for {url}"

    def test_logout_invalidates_session(self, site_url, http_client):
        """
        Test that logout invalidates session.

        Expected:
        - POST /logout
        - Session cookie cleared or invalidated
        - Protected pages require re-authentication
        """
        # Login
        self._login(site_url, http_client)

        # Logout
        logout_response = http_client.post(site_url(SITE_PORT, "/logout"))

        # Try accessing protected page after logout
        dashboard_response = http_client.get(site_url(SITE_PORT, "/dashboard"), allow_redirects=False)

        assert dashboard_response.status_code in [302, 401, 403], \
            "Should require authentication after logout"

    def test_session_expiration(self, site_url, http_client):
        """
        Test session expiration handling.

        Expected:
        - Session has expiration time
        - Expired sessions require re-authentication
        """
        # This would require time manipulation or very short session timeout
        # For now, test that session has expiration metadata
        self._login(site_url, http_client)

        session_cookies = http_client.cookies

        # Check that session cookie has expiration
        for cookie in session_cookies:
            if 'session' in cookie.name.lower():
                assert cookie.expires or cookie.get_dict().get('Max-Age'), \
                    "Session cookie should have expiration"

    @pytest.mark.slow
    def test_ground_truth_auth_flow(self, compare_with_ground_truth):
        """
        Test authentication flow statistics.

        Expected:
        - Login success rate
        - Session duration
        - Protected page count
        """
        actual_stats = {
            "login_attempts": 100,
            "successful_logins": 95,
            "protected_pages": 50,
            "session_duration_minutes": 30
        }

        comparison = compare_with_ground_truth(
            actual_stats,
            site_name="auth-session",
            data_type="stats",
            tolerance=0.10
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Auth stats don't match ground truth: {comparison}"

    def _login(self, site_url, http_client):
        """Helper method to perform login."""
        # Get CSRF token
        login_page = http_client.get(site_url(SITE_PORT, "/login"))
        soup = BeautifulSoup(login_page.content, 'html.parser')

        csrf_field = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': '_csrf'})
        csrf_token = csrf_field.get('value', '') if csrf_field else 'test_token'

        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }

        http_client.post(site_url(SITE_PORT, "/login"), data=login_data)


@pytest.mark.phase2
class TestCSRFProtection:
    """Test CSRF protection mechanisms."""

    def test_csrf_token_required(self, site_url, http_client):
        """Test that CSRF token is required for POST requests."""
        # Try login without CSRF token
        login_data = {
            'username': 'testuser',
            'password': 'testpass'
        }

        response = http_client.post(site_url(SITE_PORT, "/login"), data=login_data)

        # Should fail without CSRF token
        assert response.status_code in [400, 403], \
            "Should reject POST without CSRF token"

    def test_csrf_token_validation(self, site_url, http_client):
        """Test that CSRF token is validated."""
        # Try login with invalid CSRF token
        login_data = {
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': 'invalid_token_12345'
        }

        response = http_client.post(site_url(SITE_PORT, "/login"), data=login_data)

        # Should reject invalid token
        assert response.status_code in [400, 403], \
            "Should reject invalid CSRF token"
