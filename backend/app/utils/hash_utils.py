"""
Utility functions for generating content hashes.
Used for duplicate detection and versioning.
"""

import hashlib
from typing import Union


def generate_content_hash(content: Union[str, bytes]) -> str:
    """
    Generate SHA-256 hash of content.

    Args:
        content: String or bytes to hash

    Returns:
        Hexadecimal hash string
    """
    if isinstance(content, str):
        content = content.encode('utf-8')

    return hashlib.sha256(content).hexdigest()


def generate_hash_from_dict(data: dict, exclude_keys: list = None) -> str:
    """
    Generate hash from dictionary by converting to a sorted string.

    Args:
        data: Dictionary to hash
        exclude_keys: Keys to exclude from hash (e.g., timestamps)

    Returns:
        Hexadecimal hash string
    """
    if exclude_keys is None:
        exclude_keys = []

    # Filter out excluded keys
    filtered_data = {k: v for k, v in data.items() if k not in exclude_keys}

    # Convert to sorted string representation
    sorted_str = str(sorted(filtered_data.items()))

    return generate_content_hash(sorted_str)


def verify_hash(content: Union[str, bytes], expected_hash: str) -> bool:
    """
    Verify if content matches expected hash.

    Args:
        content: Content to verify
        expected_hash: Expected hash value

    Returns:
        True if hashes match, False otherwise
    """
    actual_hash = generate_content_hash(content)
    return actual_hash == expected_hash