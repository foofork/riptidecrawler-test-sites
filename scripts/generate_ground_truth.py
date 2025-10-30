#!/usr/bin/env python3
"""
Ground Truth Generation Script

Generates expected output files for test validation:
- <site>.pages.jsonl - List of crawled pages
- <site>.stats.json - Crawl statistics
- <site>.entities.jsonl - Extracted entities

Usage:
    python generate_ground_truth.py --site happy-path --output ground-truth/
    python generate_ground_truth.py --all
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# Site configurations
SITES_CONFIG = {
    "happy-path": {
        "port": 5001,
        "expected_pages": 110,
        "expected_entities": 100,
        "entity_type": "Event"
    },
    "redirects-canonical": {
        "port": 5002,
        "expected_pages": 50,
        "expected_entities": 50,
        "entity_type": "Event"
    },
    "robots-and-sitemaps": {
        "port": 5003,
        "expected_pages": 16,
        "expected_entities": 0,
        "entity_type": "Event"
    }
}


class GroundTruthGenerator:
    """Generates ground truth data for a test site."""

    def __init__(self, site_name: str, base_url: str = "http://localhost"):
        self.site_name = site_name
        self.config = SITES_CONFIG.get(site_name)

        if not self.config:
            raise ValueError(f"Unknown site: {site_name}")

        self.base_url = f"{base_url}:{self.config['port']}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GroundTruthGenerator/1.0'
        })

        self.visited_urls = set()
        self.pages = []
        self.entities = []
        self.stats = {
            "pages_crawled": 0,
            "pages_failed": 0,
            "domains": 1,
            "stop_reason": "completed",
            "extraction_methods": {}
        }

    def crawl(self, max_pages: Optional[int] = None):
        """
        Perform a simple crawl to generate ground truth.

        Args:
            max_pages: Maximum pages to crawl (None = unlimited)
        """
        print(f"\n🕷️  Crawling {self.site_name} at {self.base_url}")

        max_pages = max_pages or self.config["expected_pages"]
        to_visit = [self.base_url + "/"]

        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop(0)

            if url in self.visited_urls:
                continue

            print(f"  Crawling: {url}")

            try:
                response = self.session.get(url, timeout=10, allow_redirects=True)
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

                    # Parse HTML to extract links and entities
                    if 'html' in response.headers.get("Content-Type", ""):
                        soup = BeautifulSoup(response.content, 'html.parser')

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

                            # Only crawl same domain
                            if absolute_url.startswith(self.base_url):
                                if absolute_url not in self.visited_urls:
                                    to_visit.append(absolute_url)

                        # Extract entities (JSON-LD)
                        self._extract_entities(soup, response.url)

                    self.pages.append(page_data)
                else:
                    self.stats["pages_failed"] += 1

            except Exception as e:
                print(f"    ❌ Error: {e}")
                self.stats["pages_failed"] += 1

        # Update final stats
        if len(self.visited_urls) >= max_pages:
            self.stats["stop_reason"] = "max_pages"

        print(f"\n✅ Crawled {self.stats['pages_crawled']} pages")
        print(f"   Found {len(self.entities)} entities")

    def _calculate_depth(self, url: str) -> int:
        """Calculate URL depth from base URL."""
        path = urlparse(url).path.strip('/')
        return len(path.split('/')) if path else 0

    def _extract_entities(self, soup: BeautifulSoup, url: str):
        """Extract structured data entities from page."""
        # Find JSON-LD script tags
        jsonld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

        for script in jsonld_scripts:
            try:
                data = json.loads(script.string)

                # Check if it matches expected entity type
                entity_type = data.get('@type')
                if entity_type == self.config["entity_type"]:
                    entity = {
                        "type": entity_type,
                        "url": url,
                        **{k: v for k, v in data.items() if k not in ['@context', '@type']}
                    }
                    self.entities.append(entity)

            except json.JSONDecodeError:
                pass

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
        with open(pages_file, 'w') as f:
            for page in self.pages:
                f.write(json.dumps(page) + '\n')
        print(f"   ✓ {pages_file}")

        # Save stats (JSON)
        stats_file = output_dir / f"{self.site_name}.stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"   ✓ {stats_file}")

        # Save entities (JSONL)
        entities_file = output_dir / f"{self.site_name}.entities.jsonl"
        with open(entities_file, 'w') as f:
            for entity in self.entities:
                f.write(json.dumps(entity) + '\n')
        print(f"   ✓ {entities_file}")

        print(f"\n✅ Ground truth generated successfully")

    def validate(self) -> bool:
        """
        Validate generated ground truth against expected values.

        Returns:
            bool: True if validation passes
        """
        print(f"\n🔍 Validating ground truth...")

        errors = []

        # Check page count
        expected_pages = self.config["expected_pages"]
        actual_pages = self.stats["pages_crawled"]
        tolerance = int(expected_pages * 0.05)  # 5% tolerance

        if abs(actual_pages - expected_pages) > tolerance:
            errors.append(
                f"Page count mismatch: expected {expected_pages} ±{tolerance}, got {actual_pages}"
            )

        # Check entity count
        expected_entities = self.config["expected_entities"]
        actual_entities = len(self.entities)
        tolerance = int(expected_entities * 0.05)

        if abs(actual_entities - expected_entities) > tolerance:
            errors.append(
                f"Entity count mismatch: expected {expected_entities} ±{tolerance}, got {actual_entities}"
            )

        # Check entity type
        if self.entities:
            wrong_types = [e for e in self.entities if e.get('type') != self.config["entity_type"]]
            if wrong_types:
                errors.append(
                    f"Found {len(wrong_types)} entities with wrong type"
                )

        if errors:
            print(f"\n❌ Validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print(f"\n✅ Validation passed")
            return True


def generate_sitemap_coverage(site_name: str, output_dir: Path):
    """Generate sitemap coverage report."""
    config = SITES_CONFIG.get(site_name)
    if not config:
        return

    port = config["port"]
    sitemap_url = f"http://localhost:{port}/sitemap.xml"

    print(f"\n🗺️  Checking sitemap coverage for {site_name}")

    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            urls = soup.find_all('loc')

            sitemap_data = {
                "sitemap_url": sitemap_url,
                "url_count": len(urls),
                "urls": [url.text for url in urls]
            }

            # Save sitemap coverage
            output_file = output_dir / f"{site_name}.sitemap.json"
            with open(output_file, 'w') as f:
                json.dump(sitemap_data, f, indent=2)

            print(f"   ✓ Found {len(urls)} URLs in sitemap")
            print(f"   ✓ Saved to {output_file}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate ground truth data for RipTide test sites"
    )

    parser.add_argument(
        '--site',
        help='Site name (e.g., happy-path, redirects-canonical)',
        choices=list(SITES_CONFIG.keys())
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate ground truth for all Phase 1 sites'
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
        '--validate',
        action='store_true',
        help='Validate generated ground truth'
    )
    parser.add_argument(
        '--include-sitemap',
        action='store_true',
        help='Also generate sitemap coverage reports'
    )

    args = parser.parse_args()

    if not args.site and not args.all:
        parser.error("Must specify --site or --all")

    output_dir = Path(args.output)

    # Determine which sites to process
    if args.all:
        sites = list(SITES_CONFIG.keys())
    else:
        sites = [args.site]

    print("="*70)
    print("🎯 Ground Truth Generation")
    print("="*70)

    all_valid = True

    for site_name in sites:
        try:
            generator = GroundTruthGenerator(site_name, args.base_url)
            generator.crawl(max_pages=args.max_pages)
            generator.save(output_dir)

            if args.validate:
                valid = generator.validate()
                all_valid = all_valid and valid

            if args.include_sitemap:
                generate_sitemap_coverage(site_name, output_dir)

        except Exception as e:
            print(f"\n❌ Error generating ground truth for {site_name}: {e}")
            all_valid = False

    print("\n" + "="*70)
    if all_valid:
        print("✅ All ground truth files generated successfully")
        sys.exit(0)
    else:
        print("❌ Some ground truth files failed validation")
        sys.exit(1)


if __name__ == "__main__":
    main()
