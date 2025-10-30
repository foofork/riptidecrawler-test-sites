#!/usr/bin/env python3
"""
Ground Truth Batch Generation Script

Enhanced version that handles all 13 sites including complex scenarios:
- Authentication flows
- Rate limiting
- Multiple content types
- Encoding detection
- Binary content handling
- Slow responses

Usage:
    # Generate single site
    python generate_ground_truth_batch.py --site slowpoke-and-retries

    # Generate all missing sites (Phase 2 & 3)
    python generate_ground_truth_batch.py --all-missing

    # Generate all sites (re-generate Phase 1 too)
    python generate_ground_truth_batch.py --all

    # Validate only
    python generate_ground_truth_batch.py --site slowpoke-and-retries --validate-only
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ============================================================================
# SITE CONFIGURATIONS
# ============================================================================

SITES_CONFIG = {
    # Phase 1 Sites (already have ground truth)
    "happy-path": {
        "port": 5001,
        "expected_pages": 110,
        "expected_entities": 100,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 1
    },
    "redirects-canonical": {
        "port": 5005,
        "expected_pages": 50,
        "expected_entities": 50,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 1
    },
    "robots-and-sitemaps": {
        "port": 5006,
        "expected_pages": 151,
        "expected_entities": 100,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 1
    },

    # Phase 2 Sites (need ground truth)
    "slowpoke-and-retries": {
        "port": 5004,
        "expected_pages": 25,
        "expected_entities": 15,
        "entity_type": "Event",
        "timeout": 30,  # Longer timeout for slow responses
        "retry_attempts": 3,
        "retry_delay": 2,
        "rate_limit_delay": 1,  # Delay between requests
        "phase": 2
    },
    "selectors-vs-llm": {
        "port": 5005,
        "expected_pages": 10,
        "expected_entities": 10,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 2
    },
    "static-vs-headless": {
        "port": 5006,
        "expected_pages": 20,
        "expected_entities": 15,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 2,
        "note": "May include JS-rendered content detection"
    },
    "pdfs-and-binaries": {
        "port": 5007,
        "expected_pages": 15,
        "expected_entities": 5,
        "entity_type": "Document",
        "timeout": 10,
        "phase": 2,
        "note": "Only crawl HTML pages, skip binary downloads"
    },
    "auth-and-session": {
        "port": 5008,
        "expected_pages": 25,
        "expected_entities": 10,
        "entity_type": "User",
        "timeout": 10,
        "phase": 2,
        "auth_required": True,
        "auth_endpoint": "/api/login",
        "auth_credentials": {
            "username": "testuser",
            "password": "testpass"
        }
    },

    # Phase 3 Sites (need ground truth)
    "encoding-and-i18n": {
        "port": 5009,
        "expected_pages": 30,
        "expected_entities": 20,
        "entity_type": "Article",
        "timeout": 10,
        "phase": 3,
        "note": "Multiple encodings: UTF-8, ISO-8859-1, Shift-JIS, etc."
    },
    "media-and-nonhtml": {
        "port": 5010,
        "expected_pages": 25,
        "expected_entities": 15,
        "entity_type": "Article",
        "timeout": 10,
        "phase": 3,
        "note": "Multiple content types: JSON, XML, CSV, OpenGraph"
    },
    "anti-bot-lite": {
        "port": 5011,
        "expected_pages": 20,
        "expected_entities": 10,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 3,
        "rate_limit_delay": 0.5,  # 2 requests per second max
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    },
    "jobs-and-offers": {
        "port": 5012,
        "expected_pages": 60,
        "expected_entities": 50,
        "entity_type": "JobPosting",
        "timeout": 10,
        "phase": 3,
        "note": "70% messy HTML, 30% clean HTML, focus on JSON-LD"
    },
    "websocket-stream-sink": {
        "port": 5013,
        "expected_pages": 15,
        "expected_entities": 10,
        "entity_type": "Event",
        "timeout": 10,
        "phase": 3,
        "note": "Focus on HTTP endpoints only, skip WebSocket for ground truth"
    },
}


# ============================================================================
# GROUND TRUTH GENERATOR CLASS
# ============================================================================

class GroundTruthGenerator:
    """Enhanced ground truth generator with support for all site types."""

    def __init__(self, site_name: str, base_url: str = "http://localhost"):
        self.site_name = site_name
        self.config = SITES_CONFIG.get(site_name)

        if not self.config:
            raise ValueError(f"Unknown site: {site_name}. Available: {list(SITES_CONFIG.keys())}")

        self.base_url = f"{base_url}:{self.config['port']}"
        self.session = requests.Session()

        # Configure User-Agent
        user_agent = self.config.get('user_agent', 'GroundTruthGenerator/2.0 (compatible; Mozilla/5.0)')
        self.session.headers.update({'User-Agent': user_agent})

        self.visited_urls: Set[str] = set()
        self.pages: List[Dict] = []
        self.entities: List[Dict] = []
        self.stats = {
            "pages_crawled": 0,
            "pages_failed": 0,
            "domains": 1,
            "stop_reason": "completed",
            "extraction_methods": {}
        }

        self.authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with the site if required.

        Returns:
            bool: True if authentication successful or not required
        """
        if not self.config.get('auth_required'):
            return True

        print(f"  🔐 Authenticating...")

        auth_endpoint = self.config.get('auth_endpoint', '/api/login')
        auth_url = self.base_url + auth_endpoint
        credentials = self.config.get('auth_credentials', {})

        try:
            response = self.session.post(
                auth_url,
                json=credentials,
                timeout=self.config.get('timeout', 10)
            )

            if response.status_code == 200:
                self.authenticated = True
                print(f"     ✓ Authentication successful")
                return True
            else:
                print(f"     ❌ Authentication failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"     ❌ Authentication error: {e}")
            return False

    def crawl(self, max_pages: Optional[int] = None):
        """
        Perform an intelligent crawl to generate ground truth.

        Args:
            max_pages: Maximum pages to crawl (None = use site expected_pages)
        """
        print(f"\n🕷️  Crawling {self.site_name} at {self.base_url}")

        # Authenticate if needed
        if self.config.get('auth_required'):
            if not self.authenticate():
                print("  ⚠️  Continuing without authentication (will record auth failures)")

        max_pages = max_pages or self.config["expected_pages"]
        to_visit = [self.base_url + "/"]

        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop(0)

            if url in self.visited_urls:
                continue

            # Rate limiting delay
            rate_limit_delay = self.config.get('rate_limit_delay', 0)
            if rate_limit_delay > 0 and len(self.visited_urls) > 0:
                time.sleep(rate_limit_delay)

            print(f"  [{len(self.visited_urls)+1}/{max_pages}] {url}")

            try:
                response = self._fetch_with_retry(url)

                if response is None:
                    continue

                self.visited_urls.add(url)

                # Record page data
                page_data = {
                    "url": response.url,
                    "requested_url": url,
                    "depth": self._calculate_depth(url),
                    "status_code": response.status_code,
                    "content_type": response.headers.get("Content-Type", ""),
                    "content_length": len(response.content),
                    "canonical_url": None,
                    "links_count": 0
                }

                if response.status_code == 200:
                    self.stats["pages_crawled"] += 1

                    # Parse HTML content
                    if 'html' in response.headers.get("Content-Type", ""):
                        soup = self._parse_html(response)

                        if soup:
                            # Extract canonical URL
                            canonical = soup.find('link', {'rel': 'canonical'})
                            if canonical:
                                page_data["canonical_url"] = canonical.get('href')

                            # Extract links
                            links = soup.find_all('a', href=True)
                            page_data["links_count"] = len(links)

                            # Add new links to crawl queue
                            for link in links:
                                href = link['href']
                                absolute_url = urljoin(url, href)

                                # Only crawl same domain, skip binaries
                                if self._should_crawl(absolute_url):
                                    if absolute_url not in self.visited_urls:
                                        to_visit.append(absolute_url)

                            # Extract entities (JSON-LD)
                            self._extract_entities(soup, response.url)

                    self.pages.append(page_data)

                else:
                    # Record non-200 pages too (redirects, errors)
                    self.pages.append(page_data)
                    self.stats["pages_failed"] += 1

            except Exception as e:
                print(f"    ❌ Error: {e}")
                self.stats["pages_failed"] += 1

        # Update final stats
        if len(self.visited_urls) >= max_pages:
            self.stats["stop_reason"] = "max_pages"

        print(f"\n✅ Crawled {self.stats['pages_crawled']} pages successfully")
        print(f"   Found {len(self.entities)} entities")
        print(f"   Failed {self.stats['pages_failed']} pages")

    def _fetch_with_retry(self, url: str) -> Optional[requests.Response]:
        """
        Fetch URL with retry logic.

        Args:
            url: URL to fetch

        Returns:
            Response object or None if all attempts failed
        """
        timeout = self.config.get('timeout', 10)
        retry_attempts = self.config.get('retry_attempts', 1)
        retry_delay = self.config.get('retry_delay', 1)

        for attempt in range(retry_attempts):
            try:
                response = self.session.get(
                    url,
                    timeout=timeout,
                    allow_redirects=True
                )
                return response

            except requests.exceptions.Timeout:
                if attempt < retry_attempts - 1:
                    print(f"    ⏱️  Timeout, retrying ({attempt + 1}/{retry_attempts})...")
                    time.sleep(retry_delay)
                else:
                    print(f"    ❌ Timeout after {retry_attempts} attempts")
                    return None

            except Exception as e:
                if attempt < retry_attempts - 1:
                    print(f"    🔄 Error, retrying: {e}")
                    time.sleep(retry_delay)
                else:
                    print(f"    ❌ Failed after {retry_attempts} attempts: {e}")
                    return None

        return None

    def _parse_html(self, response: requests.Response) -> Optional[BeautifulSoup]:
        """
        Parse HTML with proper encoding detection.

        Args:
            response: Response object

        Returns:
            BeautifulSoup object or None
        """
        try:
            # Try to detect encoding from Content-Type header
            content_type = response.headers.get('Content-Type', '')
            encoding = response.encoding

            # For encoding-and-i18n site, respect the declared encoding
            if 'charset=' in content_type:
                declared_encoding = content_type.split('charset=')[-1].split(';')[0].strip()
                encoding = declared_encoding

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
            return soup

        except Exception as e:
            print(f"    ⚠️  HTML parsing error: {e}")
            return None

    def _should_crawl(self, url: str) -> bool:
        """
        Determine if URL should be crawled.

        Args:
            url: URL to check

        Returns:
            bool: True if should crawl
        """
        # Must be same domain
        if not url.startswith(self.base_url):
            return False

        # Skip binary file extensions for pdfs-and-binaries site
        binary_extensions = ['.pdf', '.zip', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3']
        parsed = urlparse(url)
        path = parsed.path.lower()

        if any(path.endswith(ext) for ext in binary_extensions):
            return False

        # Skip WebSocket URLs
        if url.startswith('ws://') or url.startswith('wss://'):
            return False

        return True

    def _calculate_depth(self, url: str) -> int:
        """
        Calculate URL depth from base URL.

        Args:
            url: URL to analyze

        Returns:
            int: Depth level (0 = homepage)
        """
        path = urlparse(url).path.strip('/')
        return len(path.split('/')) if path else 0

    def _extract_entities(self, soup: BeautifulSoup, url: str):
        """
        Extract structured data entities from page.

        Args:
            soup: BeautifulSoup object
            url: Page URL
        """
        # Find JSON-LD script tags
        jsonld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

        for script in jsonld_scripts:
            try:
                data = json.loads(script.string)

                # Handle both single objects and arrays
                items = data if isinstance(data, list) else [data]

                for item in items:
                    # Check if it matches expected entity type
                    entity_type = item.get('@type')
                    expected_type = self.config.get("entity_type")

                    # Be flexible with entity type matching
                    if entity_type and (entity_type == expected_type or not expected_type):
                        entity = {
                            "type": entity_type,
                            "url": url,
                            **{k: v for k, v in item.items() if k not in ['@context', '@type']}
                        }
                        self.entities.append(entity)

            except json.JSONDecodeError as e:
                print(f"    ⚠️  JSON-LD parsing error: {e}")
            except Exception as e:
                print(f"    ⚠️  Entity extraction error: {e}")

    def save(self, output_dir: Path):
        """
        Save ground truth files.

        Args:
            output_dir: Directory to save files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n💾 Saving ground truth to {output_dir}")

        # Save pages (JSONL)
        pages_file = output_dir / f"{self.site_name}.pages.jsonl"
        with open(pages_file, 'w', encoding='utf-8') as f:
            for page in self.pages:
                f.write(json.dumps(page, ensure_ascii=False) + '\n')
        print(f"   ✓ {pages_file} ({len(self.pages)} pages)")

        # Save stats (JSON)
        stats_file = output_dir / f"{self.site_name}.stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        print(f"   ✓ {stats_file}")

        # Save entities (JSONL)
        entities_file = output_dir / f"{self.site_name}.entities.jsonl"
        with open(entities_file, 'w', encoding='utf-8') as f:
            for entity in self.entities:
                f.write(json.dumps(entity, ensure_ascii=False) + '\n')
        print(f"   ✓ {entities_file} ({len(self.entities)} entities)")

        print(f"\n✅ Ground truth saved successfully")

    def validate(self) -> bool:
        """
        Validate generated ground truth against expected values.

        Returns:
            bool: True if validation passes
        """
        print(f"\n🔍 Validating ground truth for {self.site_name}...")

        errors = []

        # Check page count
        expected_pages = self.config["expected_pages"]
        actual_pages = self.stats["pages_crawled"]
        tolerance = max(int(expected_pages * 0.1), 2)  # 10% tolerance, min 2

        if abs(actual_pages - expected_pages) > tolerance:
            errors.append(
                f"Page count: expected {expected_pages} ±{tolerance}, got {actual_pages}"
            )
        else:
            print(f"   ✓ Page count: {actual_pages} (expected {expected_pages} ±{tolerance})")

        # Check entity count
        expected_entities = self.config["expected_entities"]
        actual_entities = len(self.entities)
        tolerance = max(int(expected_entities * 0.1), 2)

        if abs(actual_entities - expected_entities) > tolerance:
            errors.append(
                f"Entity count: expected {expected_entities} ±{tolerance}, got {actual_entities}"
            )
        else:
            print(f"   ✓ Entity count: {actual_entities} (expected {expected_entities} ±{tolerance})")

        # Check entity types
        if self.entities:
            expected_type = self.config.get("entity_type")
            wrong_types = [e for e in self.entities if e.get('type') != expected_type]

            if wrong_types and expected_type:
                errors.append(
                    f"Entity types: found {len(wrong_types)} with wrong type (expected '{expected_type}')"
                )
            else:
                print(f"   ✓ Entity types: all match '{expected_type}'")

        # Check file structure
        if not self.pages:
            errors.append("No pages recorded")
        else:
            print(f"   ✓ Pages structure: {len(self.pages)} pages recorded")

        # Report validation result
        if errors:
            print(f"\n❌ Validation failed with {len(errors)} error(s):")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print(f"\n✅ Validation passed")
            return True


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate ground truth data for RipTide test sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate single site:
    python generate_ground_truth_batch.py --site slowpoke-and-retries

  Generate all Phase 2 & 3 sites:
    python generate_ground_truth_batch.py --all-missing

  Generate all sites (including Phase 1):
    python generate_ground_truth_batch.py --all

  Validate only (don't regenerate):
    python generate_ground_truth_batch.py --site slowpoke-and-retries --validate-only
        """
    )

    parser.add_argument(
        '--site',
        help='Site name (e.g., slowpoke-and-retries, jobs-and-offers)',
        choices=list(SITES_CONFIG.keys())
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate ground truth for all sites (including Phase 1)'
    )
    parser.add_argument(
        '--all-missing',
        action='store_true',
        help='Generate ground truth for all Phase 2 & 3 sites (missing ground truth)'
    )
    parser.add_argument(
        '--output',
        default='ground-truth',
        help='Output directory (default: ground-truth)'
    )
    parser.add_argument(
        '--base-url',
        default='http://localhost',
        help='Base URL for sites (default: http://localhost)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum pages to crawl (default: site expected_pages)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing ground truth (don\'t regenerate)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation after generation'
    )

    args = parser.parse_args()

    # Determine which sites to process
    if args.site:
        sites = [args.site]
    elif args.all:
        sites = list(SITES_CONFIG.keys())
    elif args.all_missing:
        # Only Phase 2 & 3 sites (missing ground truth)
        sites = [name for name, config in SITES_CONFIG.items() if config['phase'] in [2, 3]]
    else:
        parser.error("Must specify --site, --all, or --all-missing")

    output_dir = Path(args.output)

    print("=" * 70)
    print("🎯 Ground Truth Batch Generation")
    print("=" * 70)
    print(f"\nProcessing {len(sites)} site(s): {', '.join(sites)}")

    all_valid = True
    results = []

    for i, site_name in enumerate(sites, 1):
        print(f"\n{'=' * 70}")
        print(f"Site {i}/{len(sites)}: {site_name}")
        print(f"{'=' * 70}")

        try:
            generator = GroundTruthGenerator(site_name, args.base_url)

            # Validate only mode
            if args.validate_only:
                # Load existing files
                pages_file = output_dir / f"{site_name}.pages.jsonl"
                entities_file = output_dir / f"{site_name}.entities.jsonl"
                stats_file = output_dir / f"{site_name}.stats.json"

                if not all(f.exists() for f in [pages_file, entities_file, stats_file]):
                    print(f"❌ Missing ground truth files for {site_name}")
                    all_valid = False
                    results.append((site_name, False, "Missing files"))
                    continue

                # Load and set data for validation
                with open(pages_file, 'r', encoding='utf-8') as f:
                    generator.pages = [json.loads(line) for line in f]

                with open(entities_file, 'r', encoding='utf-8') as f:
                    generator.entities = [json.loads(line) for line in f]

                with open(stats_file, 'r', encoding='utf-8') as f:
                    generator.stats = json.load(f)

                valid = generator.validate()
                all_valid = all_valid and valid
                results.append((site_name, valid, "Validation only"))

            else:
                # Generate mode
                generator.crawl(max_pages=args.max_pages)
                generator.save(output_dir)

                # Validate unless skipped
                if not args.skip_validation:
                    valid = generator.validate()
                    all_valid = all_valid and valid
                    results.append((site_name, valid, "Generated"))
                else:
                    results.append((site_name, True, "Generated (validation skipped)"))

        except Exception as e:
            print(f"\n❌ Error processing {site_name}: {e}")
            import traceback
            traceback.print_exc()
            all_valid = False
            results.append((site_name, False, f"Error: {e}"))

    # Final summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    for site_name, valid, note in results:
        status = "✅" if valid else "❌"
        print(f"{status} {site_name:30s} - {note}")

    print("\n" + "=" * 70)

    if all_valid:
        print("✅ All ground truth files processed successfully")
        sys.exit(0)
    else:
        print("❌ Some ground truth files failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
