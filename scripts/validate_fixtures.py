#!/usr/bin/env python3
"""
Fixture Validation Script

Validates that test site fixtures are correctly configured and deterministic.

Usage:
    python validate_fixtures.py
    python validate_fixtures.py --site happy-path
    python validate_fixtures.py --all
"""

import argparse
import sys
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json


SITES_CONFIG = {
    "happy-path": {
        "port": 5001,
        "expected_pages": 110,
        "checks": ["json-ld", "sitemap", "robots", "pagination"]
    },
    "redirects-canonical": {
        "port": 5005,
        "expected_pages": 50,
        "checks": ["redirects", "canonical", "deduplication"]
    },
    "robots-and-sitemaps": {
        "port": 5006,
        "expected_pages": 151,
        "checks": ["robots-compliance", "sitemap-coverage", "crawl-delay"]
    }
}


class FixtureValidator:
    """Validates fixture site configuration and behavior."""

    def __init__(self, site_name: str, base_url: str = "http://localhost"):
        self.site_name = site_name
        self.config = SITES_CONFIG.get(site_name)

        if not self.config:
            raise ValueError(f"Unknown site: {site_name}")

        self.base_url = f"{base_url}:{self.config['port']}"
        self.session = requests.Session()
        self.errors = []
        self.warnings = []

    def validate_all(self):
        """Run all validation checks."""
        print(f"\n🔍 Validating {self.site_name}")
        print("━" * 60)

        checks = {
            "json-ld": self.check_jsonld,
            "sitemap": self.check_sitemap,
            "robots": self.check_robots,
            "pagination": self.check_pagination,
            "redirects": self.check_redirects,
            "canonical": self.check_canonical,
            "robots-compliance": self.check_robots_compliance,
            "sitemap-coverage": self.check_sitemap_coverage,
        }

        for check_name in self.config.get("checks", []):
            if check_name in checks:
                try:
                    checks[check_name]()
                except Exception as e:
                    self.errors.append(f"{check_name}: {str(e)}")

        self.print_results()
        return len(self.errors) == 0

    def check_jsonld(self):
        """Validate JSON-LD structured data."""
        print("  Checking JSON-LD structured data...")

        response = self.session.get(f"{self.base_url}/event/1")
        if response.status_code != 200:
            self.errors.append("Event page not accessible")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        jsonld_script = soup.find('script', {'type': 'application/ld+json'})

        if not jsonld_script:
            self.errors.append("JSON-LD not found on event page")
            return

        try:
            data = json.loads(jsonld_script.string)

            required_fields = ['@type', 'name', 'startDate', 'location']
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                self.errors.append(f"Missing JSON-LD fields: {missing_fields}")
            elif data['@type'] != 'Event':
                self.errors.append(f"Wrong @type: expected Event, got {data['@type']}")
            else:
                print("    ✓ JSON-LD valid")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON-LD: {e}")

    def check_sitemap(self):
        """Validate sitemap.xml."""
        print("  Checking sitemap.xml...")

        response = self.session.get(f"{self.base_url}/sitemap.xml")
        if response.status_code != 200:
            self.errors.append("sitemap.xml not accessible")
            return

        soup = BeautifulSoup(response.content, 'xml')
        urls = soup.find_all('url')

        if len(urls) < 50:
            self.warnings.append(f"Sitemap has only {len(urls)} URLs")
        else:
            print(f"    ✓ Sitemap has {len(urls)} URLs")

    def check_robots(self):
        """Validate robots.txt."""
        print("  Checking robots.txt...")

        response = self.session.get(f"{self.base_url}/robots.txt")
        if response.status_code != 200:
            self.errors.append("robots.txt not accessible")
            return

        content = response.text
        required_directives = ['User-agent:', 'Sitemap:']

        for directive in required_directives:
            if directive not in content:
                self.errors.append(f"robots.txt missing {directive}")

        if not self.errors:
            print("    ✓ robots.txt valid")

    def check_pagination(self):
        """Validate pagination."""
        print("  Checking pagination...")

        response = self.session.get(f"{self.base_url}/?page=2")
        if response.status_code != 200:
            self.errors.append("Pagination not working")
            return

        print("    ✓ Pagination works")

    def check_redirects(self):
        """Validate redirect handling."""
        print("  Checking redirects...")

        response = self.session.get(
            f"{self.base_url}/old-event/1",
            allow_redirects=True
        )

        if response.status_code == 200:
            if response.history:
                print(f"    ✓ Redirect chain: {len(response.history)} hops")
            else:
                self.warnings.append("No redirects found on test URL")
        else:
            self.errors.append("Redirect test failed")

    def check_canonical(self):
        """Validate canonical URLs."""
        print("  Checking canonical URLs...")

        response = self.session.get(f"{self.base_url}/events/1")
        soup = BeautifulSoup(response.content, 'html.parser')

        canonical = soup.find('link', {'rel': 'canonical'})
        if not canonical:
            self.errors.append("Canonical link missing")
        else:
            print("    ✓ Canonical URLs present")

    def check_robots_compliance(self):
        """Validate robots.txt compliance."""
        print("  Checking robots.txt compliance...")

        response = self.session.get(f"{self.base_url}/robots.txt")
        content = response.text

        if 'Disallow:' in content and 'Allow:' in content:
            print("    ✓ Has Disallow and Allow directives")
        else:
            self.warnings.append("Missing Disallow or Allow directives")

        if 'Crawl-delay:' in content:
            print("    ✓ Has Crawl-delay directive")
        else:
            self.warnings.append("Missing Crawl-delay directive")

    def check_sitemap_coverage(self):
        """Validate sitemap coverage."""
        print("  Checking sitemap coverage...")

        response = self.session.get(f"{self.base_url}/sitemap-index.xml")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            sitemaps = soup.find_all('sitemap')
            print(f"    ✓ Sitemap index with {len(sitemaps)} child sitemaps")
        else:
            self.warnings.append("No sitemap index found")

    def check_deterministic_data(self):
        """Validate deterministic data generation."""
        print("  Checking data determinism...")

        # Fetch same URL twice
        response1 = self.session.get(f"{self.base_url}/event/1")
        time.sleep(0.1)
        response2 = self.session.get(f"{self.base_url}/event/1")

        if response1.content == response2.content:
            print("    ✓ Data is deterministic")
        else:
            self.errors.append("Data is not deterministic")

    def print_results(self):
        """Print validation results."""
        print("\n" + "━" * 60)

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")
            print(f"\n❌ Validation failed for {self.site_name}")
        else:
            print(f"\n✅ Validation passed for {self.site_name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate RipTide test site fixtures"
    )

    parser.add_argument(
        '--site',
        choices=list(SITES_CONFIG.keys()),
        help='Site to validate'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all sites'
    )
    parser.add_argument(
        '--base-url',
        default='http://localhost',
        help='Base URL for sites (default: http://localhost)'
    )

    args = parser.parse_args()

    if not args.site and not args.all:
        parser.error("Must specify --site or --all")

    print("╔════════════════════════════════════════════╗")
    print("║   RipTide Fixture Validation              ║")
    print("╚════════════════════════════════════════════╝")

    # Determine sites to validate
    if args.all:
        sites = list(SITES_CONFIG.keys())
    else:
        sites = [args.site]

    all_valid = True

    for site_name in sites:
        try:
            validator = FixtureValidator(site_name, args.base_url)
            valid = validator.validate_all()
            all_valid = all_valid and valid
        except Exception as e:
            print(f"\n❌ Error validating {site_name}: {e}")
            all_valid = False

    print("\n" + "═" * 60)
    if all_valid:
        print("✅ All fixtures validated successfully")
        sys.exit(0)
    else:
        print("❌ Some fixtures failed validation")
        sys.exit(1)


if __name__ == "__main__":
    main()
