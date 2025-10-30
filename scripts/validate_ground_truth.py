#!/usr/bin/env python3
"""
Ground Truth Validation Script

Validates all ground truth files for format correctness and completeness.
Can be used independently of the generation script.

Usage:
    # Validate all files
    python validate_ground_truth.py

    # Validate specific site
    python validate_ground_truth.py --site jobs-and-offers

    # Verbose output
    python validate_ground_truth.py --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Expected configurations (same as generation script)
SITES_CONFIG = {
    "happy-path": {"expected_pages": 110, "expected_entities": 100, "entity_type": "Event"},
    "redirects-canonical": {"expected_pages": 15, "expected_entities": 0, "entity_type": "Event"},
    "robots-and-sitemaps": {"expected_pages": 16, "expected_entities": 0, "entity_type": "Event"},
    "slowpoke-and-retries": {"expected_pages": 25, "expected_entities": 15, "entity_type": "Event"},
    "selectors-vs-llm": {"expected_pages": 10, "expected_entities": 10, "entity_type": "Event"},
    "static-vs-headless": {"expected_pages": 20, "expected_entities": 15, "entity_type": "Event"},
    "pdfs-and-binaries": {"expected_pages": 15, "expected_entities": 5, "entity_type": "Document"},
    "auth-and-session": {"expected_pages": 25, "expected_entities": 10, "entity_type": "User"},
    "encoding-and-i18n": {"expected_pages": 30, "expected_entities": 20, "entity_type": "Article"},
    "media-and-nonhtml": {"expected_pages": 25, "expected_entities": 15, "entity_type": "Article"},
    "anti-bot-lite": {"expected_pages": 20, "expected_entities": 10, "entity_type": "Event"},
    "jobs-and-offers": {"expected_pages": 60, "expected_entities": 50, "entity_type": "JobPosting"},
    "websocket-stream-sink": {"expected_pages": 15, "expected_entities": 10, "entity_type": "Event"},
}


# Required fields for each file type
REQUIRED_PAGE_FIELDS = {
    "url", "requested_url", "depth", "status_code",
    "content_type", "content_length", "canonical_url", "links_count"
}

REQUIRED_ENTITY_FIELDS = {"type", "url"}

REQUIRED_STATS_FIELDS = {
    "pages_crawled", "pages_failed", "domains", "stop_reason", "extraction_methods"
}


class GroundTruthValidator:
    """Validates ground truth files for correctness."""

    def __init__(self, ground_truth_dir: Path, verbose: bool = False):
        self.ground_truth_dir = Path(ground_truth_dir)
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_site(self, site_name: str) -> Tuple[bool, Dict]:
        """
        Validate all ground truth files for a site.

        Args:
            site_name: Site name to validate

        Returns:
            Tuple of (success: bool, results: Dict)
        """
        if site_name not in SITES_CONFIG:
            return False, {"error": f"Unknown site: {site_name}"}

        config = SITES_CONFIG[site_name]
        results = {
            "site": site_name,
            "files_found": {},
            "format_valid": {},
            "counts": {},
            "validation": {},
            "errors": [],
            "warnings": []
        }

        # Check file existence
        pages_file = self.ground_truth_dir / f"{site_name}.pages.jsonl"
        entities_file = self.ground_truth_dir / f"{site_name}.entities.jsonl"
        stats_file = self.ground_truth_dir / f"{site_name}.stats.json"

        results["files_found"] = {
            "pages": pages_file.exists(),
            "entities": entities_file.exists(),
            "stats": stats_file.exists()
        }

        if not all(results["files_found"].values()):
            missing = [k for k, v in results["files_found"].items() if not v]
            results["errors"].append(f"Missing files: {', '.join(missing)}")
            return False, results

        # Validate pages file
        pages_valid, pages_data = self._validate_pages_file(pages_file)
        results["format_valid"]["pages"] = pages_valid
        results["counts"]["pages"] = len(pages_data) if pages_data else 0

        # Validate entities file
        entities_valid, entities_data = self._validate_entities_file(entities_file, config)
        results["format_valid"]["entities"] = entities_valid
        results["counts"]["entities"] = len(entities_data) if entities_data else 0

        # Validate stats file
        stats_valid, stats_data = self._validate_stats_file(stats_file)
        results["format_valid"]["stats"] = stats_valid

        # Cross-validate counts
        if all(results["format_valid"].values()):
            self._validate_counts(config, pages_data, entities_data, stats_data, results)

        # Overall validation
        all_valid = all(results["format_valid"].values()) and len(results["errors"]) == 0

        return all_valid, results

    def _validate_pages_file(self, file_path: Path) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate pages JSONL file."""
        pages = []
        line_num = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_num += 1
                    if not line.strip():
                        continue

                    try:
                        page = json.loads(line)
                        pages.append(page)

                        # Check required fields
                        missing_fields = REQUIRED_PAGE_FIELDS - set(page.keys())
                        if missing_fields:
                            self.warnings.append(
                                f"{file_path.name}:{line_num} - Missing fields: {missing_fields}"
                            )

                        # Validate field types
                        if not isinstance(page.get('status_code'), int):
                            self.warnings.append(
                                f"{file_path.name}:{line_num} - status_code should be integer"
                            )

                        if not isinstance(page.get('depth'), int):
                            self.warnings.append(
                                f"{file_path.name}:{line_num} - depth should be integer"
                            )

                    except json.JSONDecodeError as e:
                        self.errors.append(
                            f"{file_path.name}:{line_num} - JSON parse error: {e}"
                        )
                        return False, None

            if self.verbose:
                print(f"  ✓ Pages file: {len(pages)} entries")

            return True, pages

        except Exception as e:
            self.errors.append(f"{file_path.name} - Error reading file: {e}")
            return False, None

    def _validate_entities_file(
        self,
        file_path: Path,
        config: Dict
    ) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate entities JSONL file."""
        entities = []
        line_num = 0
        expected_type = config.get("entity_type")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_num += 1
                    if not line.strip():
                        continue

                    try:
                        entity = json.loads(line)
                        entities.append(entity)

                        # Check required fields
                        missing_fields = REQUIRED_ENTITY_FIELDS - set(entity.keys())
                        if missing_fields:
                            self.warnings.append(
                                f"{file_path.name}:{line_num} - Missing fields: {missing_fields}"
                            )

                        # Validate entity type
                        entity_type = entity.get('type')
                        if entity_type != expected_type:
                            self.warnings.append(
                                f"{file_path.name}:{line_num} - Expected type '{expected_type}', got '{entity_type}'"
                            )

                    except json.JSONDecodeError as e:
                        self.errors.append(
                            f"{file_path.name}:{line_num} - JSON parse error: {e}"
                        )
                        return False, None

            if self.verbose:
                print(f"  ✓ Entities file: {len(entities)} entries")

            return True, entities

        except Exception as e:
            self.errors.append(f"{file_path.name} - Error reading file: {e}")
            return False, None

    def _validate_stats_file(self, file_path: Path) -> Tuple[bool, Optional[Dict]]:
        """Validate stats JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                stats = json.load(f)

            # Check required fields
            missing_fields = REQUIRED_STATS_FIELDS - set(stats.keys())
            if missing_fields:
                self.errors.append(
                    f"{file_path.name} - Missing fields: {missing_fields}"
                )
                return False, None

            # Validate field types
            if not isinstance(stats.get('pages_crawled'), int):
                self.errors.append(
                    f"{file_path.name} - pages_crawled should be integer"
                )

            if not isinstance(stats.get('pages_failed'), int):
                self.errors.append(
                    f"{file_path.name} - pages_failed should be integer"
                )

            if self.verbose:
                print(f"  ✓ Stats file: {stats['pages_crawled']} pages crawled")

            return True, stats

        except json.JSONDecodeError as e:
            self.errors.append(f"{file_path.name} - JSON parse error: {e}")
            return False, None
        except Exception as e:
            self.errors.append(f"{file_path.name} - Error reading file: {e}")
            return False, None

    def _validate_counts(
        self,
        config: Dict,
        pages: List[Dict],
        entities: List[Dict],
        stats: Dict,
        results: Dict
    ):
        """Validate counts against expected values."""
        # Page count validation
        expected_pages = config["expected_pages"]
        actual_pages = len(pages)
        tolerance = max(int(expected_pages * 0.1), 2)

        results["validation"]["pages"] = {
            "expected": expected_pages,
            "actual": actual_pages,
            "tolerance": tolerance,
            "valid": abs(actual_pages - expected_pages) <= tolerance
        }

        if not results["validation"]["pages"]["valid"]:
            results["warnings"].append(
                f"Page count outside tolerance: expected {expected_pages} ±{tolerance}, got {actual_pages}"
            )

        # Entity count validation
        expected_entities = config["expected_entities"]
        actual_entities = len(entities)
        tolerance = max(int(expected_entities * 0.1), 2)

        results["validation"]["entities"] = {
            "expected": expected_entities,
            "actual": actual_entities,
            "tolerance": tolerance,
            "valid": abs(actual_entities - expected_entities) <= tolerance
        }

        if not results["validation"]["entities"]["valid"]:
            results["warnings"].append(
                f"Entity count outside tolerance: expected {expected_entities} ±{tolerance}, got {actual_entities}"
            )

        # Stats consistency
        stats_pages = stats.get("pages_crawled", 0)
        if stats_pages != actual_pages:
            results["warnings"].append(
                f"Stats mismatch: stats.pages_crawled={stats_pages}, actual pages={actual_pages}"
            )

    def validate_all(self) -> Dict:
        """
        Validate all ground truth files.

        Returns:
            Dict with validation results for all sites
        """
        results = {
            "total_sites": len(SITES_CONFIG),
            "sites": {},
            "summary": {
                "valid": 0,
                "invalid": 0,
                "missing": 0
            }
        }

        for site_name in SITES_CONFIG.keys():
            valid, site_results = self.validate_site(site_name)

            results["sites"][site_name] = site_results

            if not all(site_results["files_found"].values()):
                results["summary"]["missing"] += 1
            elif valid:
                results["summary"]["valid"] += 1
            else:
                results["summary"]["invalid"] += 1

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate ground truth files for RipTide test sites"
    )

    parser.add_argument(
        '--site',
        help='Validate specific site only',
        choices=list(SITES_CONFIG.keys())
    )
    parser.add_argument(
        '--ground-truth-dir',
        default='ground-truth',
        help='Ground truth directory (default: ground-truth)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    ground_truth_dir = Path(args.ground_truth_dir)

    if not ground_truth_dir.exists():
        print(f"❌ Ground truth directory not found: {ground_truth_dir}")
        sys.exit(1)

    validator = GroundTruthValidator(ground_truth_dir, verbose=args.verbose)

    print("=" * 70)
    print("🔍 Ground Truth Validation")
    print("=" * 70)

    if args.site:
        # Validate single site
        print(f"\nValidating: {args.site}")
        valid, results = validator.validate_site(args.site)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_site_results(args.site, results, verbose=args.verbose)

        sys.exit(0 if valid else 1)

    else:
        # Validate all sites
        results = validator.validate_all()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_all_results(results, verbose=args.verbose)

        all_valid = results["summary"]["invalid"] == 0 and results["summary"]["missing"] == 0
        sys.exit(0 if all_valid else 1)


def print_site_results(site_name: str, results: Dict, verbose: bool = False):
    """Print validation results for a single site."""
    print("\n" + "-" * 70)

    # Files found
    print("\n📁 Files:")
    for file_type, found in results["files_found"].items():
        status = "✓" if found else "✗"
        print(f"  {status} {file_type}")

    if not all(results["files_found"].values()):
        return

    # Format validation
    print("\n📝 Format:")
    for file_type, valid in results["format_valid"].items():
        status = "✓" if valid else "✗"
        count = results["counts"].get(file_type, 0)
        print(f"  {status} {file_type}: {count} entries")

    # Count validation
    if results.get("validation"):
        print("\n📊 Validation:")
        for data_type, validation in results["validation"].items():
            if validation["valid"]:
                status = "✓"
            else:
                status = "⚠️"
            print(f"  {status} {data_type}: {validation['actual']} "
                  f"(expected {validation['expected']} ±{validation['tolerance']})")

    # Errors and warnings
    if results.get("errors"):
        print("\n❌ Errors:")
        for error in results["errors"]:
            print(f"  - {error}")

    if results.get("warnings") and verbose:
        print("\n⚠️  Warnings:")
        for warning in results["warnings"]:
            print(f"  - {warning}")

    # Overall status
    all_valid = (
        all(results["format_valid"].values()) and
        len(results["errors"]) == 0 and
        all(v["valid"] for v in results.get("validation", {}).values())
    )

    print("\n" + "-" * 70)
    if all_valid:
        print("✅ PASSED")
    else:
        print("❌ FAILED")


def print_all_results(results: Dict, verbose: bool = False):
    """Print validation results for all sites."""
    print(f"\nValidating {results['total_sites']} sites...")
    print()

    # Print results for each site
    for site_name, site_results in results["sites"].items():
        files_ok = all(site_results["files_found"].values())
        format_ok = all(site_results["format_valid"].values()) if files_ok else False
        validation_ok = all(
            v["valid"] for v in site_results.get("validation", {}).values()
        ) if files_ok else False
        errors_ok = len(site_results.get("errors", [])) == 0

        if files_ok and format_ok and validation_ok and errors_ok:
            status = "✅"
        elif not files_ok:
            status = "❓"
        else:
            status = "❌"

        pages = site_results["counts"].get("pages", 0)
        entities = site_results["counts"].get("entities", 0)

        print(f"{status} {site_name:30s} - {pages:3d} pages, {entities:3d} entities")

        if verbose and site_results.get("warnings"):
            for warning in site_results["warnings"][:3]:  # Show first 3 warnings
                print(f"    ⚠️  {warning}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"  ✅ Valid:   {results['summary']['valid']}")
    print(f"  ❌ Invalid: {results['summary']['invalid']}")
    print(f"  ❓ Missing: {results['summary']['missing']}")
    print("=" * 70)

    if results['summary']['invalid'] == 0 and results['summary']['missing'] == 0:
        print("✅ ALL SITES VALIDATED SUCCESSFULLY")
    else:
        print("❌ SOME SITES FAILED VALIDATION")


if __name__ == "__main__":
    main()
