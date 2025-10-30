"""
Pytest Configuration and Fixtures for RipTide Test Sites

Provides shared fixtures for:
- Docker health checks
- Ground truth comparison utilities
- HTTP client setup
- Test data management
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Test configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost")
FIXTURE_SEED = int(os.getenv("FIXTURE_SEED", "42"))
TEST_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "30"))
GROUND_TRUTH_DIR = Path(__file__).parent.parent / "ground-truth"


@pytest.fixture(scope="session")
def docker_services():
    """
    Ensures Docker Compose services are running for the test session.

    Validates that all required sites are healthy before running tests.
    """
    # Check if services are already running
    result = subprocess.run(
        ["docker-compose", "ps", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    if not result.stdout.strip():
        # Services not running, start them
        print("\n🚀 Starting Docker Compose services...")
        subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            check=True,
            cwd=Path(__file__).parent.parent
        )

        # Wait for services to be healthy
        time.sleep(10)

    yield

    # Optionally tear down services after tests
    # Uncomment if you want automatic cleanup
    # subprocess.run(["docker-compose", "down"], cwd=Path(__file__).parent.parent)


@pytest.fixture(scope="session")
def http_client():
    """
    Provides a configured HTTP client with retries and timeouts.

    Returns:
        requests.Session: Configured session with retry logic
    """
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "HEAD"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set default timeout
    session.timeout = TEST_TIMEOUT

    return session


@pytest.fixture
def health_check(http_client):
    """
    Factory fixture for checking site health.

    Usage:
        health_check(5001)  # Check happy-path.site
        health_check(5002, path="/health")  # Custom health endpoint
    """
    def check(port: int, path: str = "/health", expected_status: int = 200, timeout: int = 5) -> bool:
        """
        Check if a site is healthy.

        Args:
            port: Port number to check
            path: URL path to check
            expected_status: Expected HTTP status code

        Returns:
            bool: True if healthy, False otherwise
        """
        url = f"{BASE_URL}:{port}{path}"
        try:
            response = http_client.get(url, timeout=timeout)
            is_healthy = response.status_code == expected_status

            if is_healthy:
                print(f"✅ Site on port {port} is healthy")
            else:
                print(f"❌ Site on port {port} returned {response.status_code}")

            return is_healthy
        except Exception as e:
            print(f"❌ Site on port {port} health check failed: {e}")
            return False

    return check


@pytest.fixture
def ground_truth_loader():
    """
    Loads ground truth data for comparison.

    Usage:
        pages = ground_truth_loader("happy-path", "pages")
        stats = ground_truth_loader("happy-path", "stats")
        entities = ground_truth_loader("happy-path", "entities")
    """
    def load(site_name: str, data_type: str) -> Optional[Dict]:
        """
        Load ground truth data from file.

        Args:
            site_name: Name of the site (e.g., "happy-path")
            data_type: Type of data ("pages", "stats", or "entities")

        Returns:
            Dict or List: Loaded data, or None if file not found
        """
        file_ext = "json" if data_type == "stats" else "jsonl"
        file_path = GROUND_TRUTH_DIR / f"{site_name}.{data_type}.{file_ext}"

        if not file_path.exists():
            print(f"⚠️  Ground truth file not found: {file_path}")
            return None

        if data_type == "stats":
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Load JSONL (one JSON object per line)
            with open(file_path, 'r') as f:
                return [json.loads(line) for line in f if line.strip()]

    return load


@pytest.fixture
def compare_with_ground_truth(ground_truth_loader):
    """
    Compares test results with ground truth data.

    Usage:
        result = compare_with_ground_truth(
            actual_data,
            site_name="happy-path",
            data_type="pages",
            tolerance=0.05  # 5% variance allowed
        )
    """
    def compare(
        actual: Dict or List,
        site_name: str,
        data_type: str,
        tolerance: float = 0.05,
        strict: bool = False
    ) -> Dict:
        """
        Compare actual results with ground truth.

        Args:
            actual: Actual data from test
            site_name: Name of the site
            data_type: Type of data
            tolerance: Allowed variance (0.05 = 5%)
            strict: If True, fail on any mismatch

        Returns:
            Dict with comparison results
        """
        expected = ground_truth_loader(site_name, data_type)

        if expected is None:
            return {
                "status": "no_ground_truth",
                "message": f"Ground truth not found for {site_name}.{data_type}"
            }

        comparison = {
            "status": "pass",
            "differences": [],
            "summary": {}
        }

        if data_type == "stats":
            # Compare statistics
            for key in expected:
                actual_value = actual.get(key)
                expected_value = expected[key]

                if isinstance(expected_value, (int, float)):
                    # Allow tolerance for numeric values
                    allowed_range = abs(expected_value * tolerance)
                    # Handle None values before arithmetic
                    if actual_value is None or abs(actual_value - expected_value) > allowed_range:
                        comparison["differences"].append({
                            "key": key,
                            "expected": expected_value,
                            "actual": actual_value,
                            "tolerance": allowed_range
                        })
                elif actual_value != expected_value:
                    comparison["differences"].append({
                        "key": key,
                        "expected": expected_value,
                        "actual": actual_value
                    })

            comparison["summary"] = {
                "total_keys": len(expected),
                "matching_keys": len(expected) - len(comparison["differences"]),
                "differing_keys": len(comparison["differences"])
            }

        elif data_type in ["pages", "entities"]:
            # Compare lists
            actual_count = len(actual)
            expected_count = len(expected)

            comparison["summary"] = {
                "expected_count": expected_count,
                "actual_count": actual_count,
                "count_difference": abs(actual_count - expected_count)
            }

            # Check if count is within tolerance
            allowed_diff = int(expected_count * tolerance)
            if abs(actual_count - expected_count) > allowed_diff:
                comparison["differences"].append({
                    "type": "count_mismatch",
                    "expected": expected_count,
                    "actual": actual_count,
                    "allowed_difference": allowed_diff
                })

        # Determine status
        if comparison["differences"]:
            comparison["status"] = "fail" if strict else "warning"

        return comparison

    return compare


@pytest.fixture
def site_url():
    """
    Factory fixture for generating site URLs.

    Usage:
        url = site_url(5001, "/events/")
    """
    def generate(port: int, path: str = "/") -> str:
        """Generate full URL for a site."""
        return f"{BASE_URL}:{port}{path}"

    return generate


@pytest.fixture
def crawl_simulator(http_client):
    """
    Simulates a basic web crawler for testing.

    Returns:
        Function that performs a simple crawl
    """
    def crawl(start_url: str, max_pages: int = 10) -> Dict:
        """
        Perform a simple breadth-first crawl.

        Args:
            start_url: Starting URL
            max_pages: Maximum pages to crawl

        Returns:
            Dict with crawl results
        """
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse
        except ImportError:
            # If BeautifulSoup not available, return minimal crawl
            print("Warning: BeautifulSoup not installed, returning minimal crawl")
            try:
                response = http_client.get(start_url, timeout=10)
                return {
                    "pages_crawled": 1,
                    "pages": [{
                        "url": start_url,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("Content-Type", ""),
                        "content_length": len(response.content)
                    }],
                    "start_url": start_url
                }
            except:
                return {"pages_crawled": 0, "pages": [], "start_url": start_url}

        visited = set()
        to_visit = [start_url]
        pages = []
        base_domain = urlparse(start_url).netloc

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            try:
                response = http_client.get(url, timeout=10)
                visited.add(url)

                page_data = {
                    "url": url,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("Content-Type", ""),
                    "content_length": len(response.content)
                }

                pages.append(page_data)

                # Parse HTML and extract links if content is HTML
                content_type = response.headers.get("Content-Type", "")
                if response.status_code == 200 and "text/html" in content_type:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']

                        # Convert relative URLs to absolute
                        absolute_url = urljoin(url, href)

                        # Only follow links on the same domain
                        parsed = urlparse(absolute_url)
                        if parsed.netloc == base_domain:
                            # Remove fragment and query for deduplication
                            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                            if clean_url not in visited and clean_url not in to_visit:
                                to_visit.append(clean_url)

            except Exception as e:
                print(f"Error crawling {url}: {e}")

        return {
            "pages_crawled": len(pages),
            "pages": pages,
            "start_url": start_url
        }

    return crawl


# Markers for categorizing tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "phase1: Phase 1 sites (happy-path, redirects, robots)"
    )
    config.addinivalue_line(
        "markers", "phase2: Phase 2 sites (slowpoke, selectors, etc.)"
    )
    config.addinivalue_line(
        "markers", "phase3: Phase 3 sites (i18n, websocket, etc.)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that may take >10 seconds"
    )
    config.addinivalue_line(
        "markers", "requires_docker: Tests that require Docker services"
    )


# Session-wide setup
@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Validates test environment before running tests.
    """
    print("\n" + "="*70)
    print("🧪 RipTide Test Sites - Testing Environment")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Fixture Seed: {FIXTURE_SEED}")
    print(f"Test Timeout: {TEST_TIMEOUT}s")
    print(f"Ground Truth Dir: {GROUND_TRUTH_DIR}")
    print("="*70 + "\n")

    yield

    print("\n" + "="*70)
    print("✅ Test session completed")
    print("="*70 + "\n")
