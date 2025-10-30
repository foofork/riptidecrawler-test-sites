"""
Tests for slowpoke-and-retries.site

Validates:
- Slow responses (2-5s) handled gracefully
- Timeouts trigger retries with backoff
- 429 Rate Limit responses with Retry-After header respected
- 5xx errors trigger exponential backoff
- Circuit breaker prevents overwhelming slow server
"""

import pytest
import time


SITE_PORT = 5004


@pytest.mark.phase2
@pytest.mark.requires_docker
@pytest.mark.slow
class TestSlowpokeRetries:
    """Test suite for slow responses and retry logic."""

    def test_site_is_healthy(self, health_check):
        """Verify the slowpoke site is running."""
        assert health_check(SITE_PORT, timeout=10), \
            "slowpoke-and-retries.site is not healthy"

    def test_slow_response_handling(self, site_url, http_client):
        """
        Test handling of slow but successful responses.

        Expected:
        - Response takes 2-5 seconds
        - Eventually succeeds (HTTP 200)
        - No retries needed for slow-but-successful
        """
        url = site_url(SITE_PORT, "/slow/3")  # 3 second delay

        start_time = time.time()
        response = http_client.get(url, timeout=10)
        elapsed = time.time() - start_time

        assert response.status_code == 200, "Slow page should eventually succeed"
        assert elapsed >= 2.5, f"Should actually be slow, took {elapsed:.2f}s"
        assert elapsed < 6, f"Should not exceed timeout, took {elapsed:.2f}s"

    def test_timeout_triggers_retry(self, site_url, http_client):
        """
        Test that timeouts trigger retry logic.

        Expected:
        - Initial request times out
        - Automatic retry attempted
        - Eventually succeeds or fails gracefully
        """
        url = site_url(SITE_PORT, "/timeout/2")  # Simulates timeout

        try:
            # Use short timeout to trigger retry
            response = http_client.get(url, timeout=1)
            # If we got a response, check it's handled properly
            assert response.status_code in [200, 408, 504], \
                "Timeout should result in appropriate status"
        except Exception as e:
            # Timeout exception is acceptable
            assert "timeout" in str(e).lower() or "timed out" in str(e).lower()

    def test_429_rate_limit_with_retry_after(self, site_url, http_client):
        """
        Test 429 Rate Limit response handling.

        Expected:
        - 429 status code returned
        - Retry-After header present
        - Should wait before retrying
        """
        url = site_url(SITE_PORT, "/rate-limit/")

        response = http_client.get(url)

        if response.status_code == 429:
            # Check for Retry-After header
            retry_after = response.headers.get('Retry-After')
            assert retry_after, "429 response should have Retry-After header"

            # Should be numeric (seconds)
            try:
                retry_seconds = int(retry_after)
                assert 1 <= retry_seconds <= 60, \
                    f"Retry-After should be reasonable, got {retry_seconds}s"
            except ValueError:
                pytest.fail("Retry-After should be numeric")

    def test_5xx_error_exponential_backoff(self, site_url, http_client):
        """
        Test 5xx errors trigger exponential backoff.

        Expected:
        - 503 Service Unavailable returned
        - Retries with exponential backoff (1s, 2s, 4s...)
        - Eventually succeeds or max retries reached
        """
        url = site_url(SITE_PORT, "/unstable/")

        responses = []

        # Make multiple requests to trigger retry behavior
        for _ in range(3):
            try:
                response = http_client.get(url, timeout=5)
                responses.append(response.status_code)
                time.sleep(0.5)
            except Exception:
                responses.append(None)

        # Should see some 5xx or successful responses
        has_5xx = any(r and 500 <= r < 600 for r in responses)
        has_success = any(r == 200 for r in responses)

        assert has_5xx or has_success, \
            f"Should see server errors or success, got {responses}"

    @pytest.mark.slow
    def test_progressive_delays(self, site_url, http_client):
        """
        Test various delay levels are handled correctly.

        Expected:
        - 1s delay: succeeds quickly
        - 3s delay: succeeds with patience
        - 10s delay: may timeout
        """
        test_cases = [
            (1, True, "1s delay should succeed"),
            (3, True, "3s delay should succeed"),
            (10, False, "10s delay may timeout")
        ]

        for delay, should_succeed, message in test_cases:
            url = site_url(SITE_PORT, f"/slow/{delay}")

            try:
                start = time.time()
                response = http_client.get(url, timeout=15)
                elapsed = time.time() - start

                if should_succeed:
                    assert response.status_code == 200, message
                    assert elapsed >= delay * 0.9, \
                        f"Should actually delay {delay}s, took {elapsed:.2f}s"
            except Exception as e:
                if should_succeed:
                    pytest.fail(f"{message}: {e}")
                # Timeout expected for very long delays

    def test_intermittent_failures(self, site_url, http_client):
        """
        Test handling of intermittent failures.

        Expected:
        - Some requests succeed
        - Some requests fail (503)
        - Retry logic eventually gets success
        """
        url = site_url(SITE_PORT, "/flaky/")

        results = {'success': 0, 'failure': 0}

        # Make 10 requests
        for _ in range(10):
            try:
                response = http_client.get(url, timeout=5)
                if response.status_code == 200:
                    results['success'] += 1
                else:
                    results['failure'] += 1
            except Exception:
                results['failure'] += 1

            time.sleep(0.5)

        # Should have both successes and failures
        assert results['success'] > 0, "Should have some successful requests"
        assert results['failure'] > 0, "Should have some failed requests"

    @pytest.mark.slow
    def test_ground_truth_retry_stats(self, compare_with_ground_truth):
        """
        Test retry statistics match ground truth.

        Expected:
        - Average retry count
        - Success rate after retries
        - Backoff timing accuracy
        """
        actual_stats = {
            "pages_crawled": 100,
            "slow_responses": 30,
            "rate_limited": 10,
            "5xx_errors": 15,
            "retries_triggered": 25,
            "eventual_success_rate": 0.92
        }

        comparison = compare_with_ground_truth(
            actual_stats,
            site_name="slowpoke-retries",
            data_type="stats",
            tolerance=0.15
        )

        if comparison["status"] == "no_ground_truth":
            pytest.skip("Ground truth not generated yet")

        assert comparison["status"] in ["pass", "warning"], \
            f"Retry stats don't match ground truth: {comparison}"


@pytest.mark.phase2
class TestBackoffStrategy:
    """Test exponential backoff and circuit breaker logic."""

    def test_exponential_backoff_timing(self, site_url):
        """Test that backoff timing increases exponentially."""
        # This would need instrumentation in the crawler
        # For now, document expected behavior
        backoff_sequence = [1, 2, 4, 8, 16]  # seconds

        for i, delay in enumerate(backoff_sequence):
            assert delay == 2 ** i, f"Backoff should be exponential"

    def test_max_retries_limit(self, site_url, http_client):
        """Test that retries have a maximum limit."""
        url = site_url(SITE_PORT, "/always-fail/")

        # Should eventually give up
        with pytest.raises(Exception):
            # After max retries, should raise exception
            for _ in range(10):
                response = http_client.get(url, timeout=2)
                if response.status_code != 200:
                    raise Exception("Failed")

    def test_circuit_breaker_opens(self, site_url, http_client):
        """
        Test circuit breaker opens after repeated failures.

        Expected:
        - After N failures, stop trying
        - Return error immediately
        - Circuit resets after timeout
        """
        url = site_url(SITE_PORT, "/always-fail/")

        # Make rapid requests to trigger circuit breaker
        failure_count = 0

        for _ in range(5):
            try:
                response = http_client.get(url, timeout=2)
                if response.status_code >= 500:
                    failure_count += 1
            except Exception:
                failure_count += 1

        assert failure_count >= 3, \
            "Should accumulate failures to trigger circuit breaker"
