"""Ground truth comparison utilities."""

from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher


class ComparisonEngine:
    """Engine for comparing test results with ground truth."""

    def __init__(self, tolerance: float = 0.05):
        """
        Initialize comparison engine.

        Args:
            tolerance: Allowed variance (0.05 = 5%)
        """
        self.tolerance = tolerance

    def compare_stats(self, actual: Dict, expected: Dict) -> Dict:
        """
        Compare statistics dictionaries.

        Args:
            actual: Actual statistics
            expected: Expected statistics

        Returns:
            Comparison results
        """
        differences = []

        for key in expected:
            if key not in actual:
                differences.append({
                    'key': key,
                    'issue': 'missing',
                    'expected': expected[key]
                })
                continue

            actual_value = actual[key]
            expected_value = expected[key]

            if isinstance(expected_value, (int, float)):
                # Numeric comparison with tolerance
                allowed_diff = abs(expected_value * self.tolerance)
                diff = abs(actual_value - expected_value)

                if diff > allowed_diff:
                    differences.append({
                        'key': key,
                        'expected': expected_value,
                        'actual': actual_value,
                        'difference': diff,
                        'allowed_difference': allowed_diff
                    })
            else:
                # Exact comparison for non-numeric
                if actual_value != expected_value:
                    differences.append({
                        'key': key,
                        'expected': expected_value,
                        'actual': actual_value
                    })

        return {
            'passed': len(differences) == 0,
            'total_keys': len(expected),
            'matching_keys': len(expected) - len(differences),
            'differences': differences
        }

    def compare_lists(self, actual: List, expected: List) -> Dict:
        """
        Compare lists with tolerance.

        Args:
            actual: Actual list
            expected: Expected list

        Returns:
            Comparison results
        """
        actual_count = len(actual)
        expected_count = len(expected)
        allowed_diff = int(expected_count * self.tolerance)

        count_match = abs(actual_count - expected_count) <= allowed_diff

        return {
            'passed': count_match,
            'expected_count': expected_count,
            'actual_count': actual_count,
            'difference': abs(actual_count - expected_count),
            'allowed_difference': allowed_diff
        }

    def compare_entities(self, actual: List[Dict], expected: List[Dict]) -> Dict:
        """
        Compare extracted entities.

        Args:
            actual: Actual entities
            expected: Expected entities

        Returns:
            Comparison results
        """
        # First compare counts
        count_result = self.compare_lists(actual, expected)

        if not count_result['passed']:
            return {
                'passed': False,
                'reason': 'count_mismatch',
                **count_result
            }

        # Compare entity types
        actual_types = set(e.get('type', 'Unknown') for e in actual)
        expected_types = set(e.get('type', 'Unknown') for e in expected)

        if actual_types != expected_types:
            return {
                'passed': False,
                'reason': 'type_mismatch',
                'expected_types': list(expected_types),
                'actual_types': list(actual_types)
            }

        return {
            'passed': True,
            'entity_count': len(actual),
            'entity_types': list(actual_types)
        }


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    return SequenceMatcher(None, str1, str2).ratio()


def deep_compare(obj1: Any, obj2: Any, path: str = "") -> List[str]:
    """
    Deep comparison of nested structures.

    Args:
        obj1: First object
        obj2: Second object
        path: Current path (for error reporting)

    Returns:
        List of difference descriptions
    """
    differences = []

    if type(obj1) != type(obj2):
        differences.append(f"{path}: Type mismatch - {type(obj1).__name__} vs {type(obj2).__name__}")
        return differences

    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key

            if key not in obj1:
                differences.append(f"{new_path}: Missing in first object")
            elif key not in obj2:
                differences.append(f"{new_path}: Missing in second object")
            else:
                differences.extend(deep_compare(obj1[key], obj2[key], new_path))

    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            differences.append(f"{path}: Length mismatch - {len(obj1)} vs {len(obj2)}")
        else:
            for i in range(len(obj1)):
                new_path = f"{path}[{i}]"
                differences.extend(deep_compare(obj1[i], obj2[i], new_path))

    else:
        if obj1 != obj2:
            differences.append(f"{path}: Value mismatch - {obj1} vs {obj2}")

    return differences
