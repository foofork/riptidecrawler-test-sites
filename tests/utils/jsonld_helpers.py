"""JSON-LD extraction and validation utilities."""

import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


def extract_jsonld(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract all JSON-LD structured data from HTML.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of parsed JSON-LD objects
    """
    jsonld_data = []

    scripts = soup.find_all('script', {'type': 'application/ld+json'})

    for script in scripts:
        try:
            data = json.loads(script.string)
            jsonld_data.append(data)
        except json.JSONDecodeError:
            pass  # Skip malformed JSON-LD

    return jsonld_data


def validate_schema(data: Dict, schema_type: str, required_fields: List[str]) -> Dict:
    """
    Validate JSON-LD against expected schema.

    Args:
        data: JSON-LD data
        schema_type: Expected @type (e.g., "Event", "Product")
        required_fields: List of required field names

    Returns:
        Validation results
    """
    errors = []

    # Check @type
    actual_type = data.get('@type')
    if actual_type != schema_type:
        errors.append(f"Type mismatch: expected '{schema_type}', got '{actual_type}'")

    # Check required fields
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
        elif data[field] is None or data[field] == '':
            errors.append(f"Empty required field: '{field}'")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'data': data
    }


def extract_entities(html_content: str, entity_type: Optional[str] = None) -> List[Dict]:
    """
    Extract entities of specific type from HTML.

    Args:
        html_content: HTML content as string
        entity_type: Filter by @type (None = all types)

    Returns:
        List of entities
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    all_jsonld = extract_jsonld(soup)

    if entity_type:
        return [data for data in all_jsonld if data.get('@type') == entity_type]

    return all_jsonld


def extract_canonical_url(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract canonical URL from HTML.

    Args:
        soup: BeautifulSoup object

    Returns:
        Canonical URL or None
    """
    canonical = soup.find('link', {'rel': 'canonical'})

    if canonical:
        return canonical.get('href')

    return None


# Schema validation presets
SCHEMA_PRESETS = {
    'Event': ['name', 'startDate', 'location'],
    'Product': ['name', 'description', 'offers'],
    'Article': ['headline', 'author', 'datePublished'],
    'JobPosting': ['title', 'hiringOrganization', 'jobLocation'],
    'Recipe': ['name', 'recipeIngredient', 'recipeInstructions'],
}


def validate_event_schema(data: Dict) -> Dict:
    """Validate Event schema specifically."""
    return validate_schema(data, 'Event', SCHEMA_PRESETS['Event'])


def validate_product_schema(data: Dict) -> Dict:
    """Validate Product schema specifically."""
    return validate_schema(data, 'Product', SCHEMA_PRESETS['Product'])


def validate_article_schema(data: Dict) -> Dict:
    """Validate Article schema specifically."""
    return validate_schema(data, 'Article', SCHEMA_PRESETS['Article'])


def validate_job_schema(data: Dict) -> Dict:
    """Validate JobPosting schema specifically."""
    return validate_schema(data, 'JobPosting', SCHEMA_PRESETS['JobPosting'])
