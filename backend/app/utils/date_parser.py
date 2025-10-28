"""
Utility functions for parsing and handling dates.
Extracts dates from text and standardizes date formats.
"""

import re
from datetime import datetime
from typing import List, Optional
from dateutil import parser as date_parser
import logging

logger = logging.getLogger(__name__)


# Common date patterns
DATE_PATTERNS = [
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 12/31/2025 or 12-31-2025
    r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # 2025-12-31
    r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',  # 15 January 2025
    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}',  # January 15, 2025
]


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse the date string to datetime object.
    Handles multiple date formats.

    Args:
        date_string: Date string in various formats

    Returns:
        datetime object or None if parsing fails
    """
    if not date_string:
        return None

    try:
        # Use dateutil parser for flexible parsing
        return date_parser.parse(date_string, fuzzy=True)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse date '{date_string}': {e}")
        return None


def extract_dates_from_text(text: str) -> List[datetime]:
    """
    Extract all dates from text content.

    Args:
        text: Text content to search for dates

    Returns:
        List of datetime objects found in text
    """
    dates = []

    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            parsed_date = parse_date(match)
            if parsed_date:
                dates.append(parsed_date)

    # Remove duplicates and sort
    dates = list(set(dates))
    dates.sort()

    return dates


def format_date_iso(dt: datetime) -> str:
    """
    Format datetime to ISO 8601 string.

    Args:
        dt: datetime object

    Returns:
        ISO formatted date string
    """
    return dt.isoformat()


def format_date_display(dt: datetime) -> str:
    """
    Format datetime for display to users.

    Args:
        dt: datetime object

    Returns:
        Formatted date string (e.g., "November 3, 2025")
    """
    return dt.strftime("%B %d, %Y")


def parse_date_range(from_date: Optional[str], to_date: Optional[str]) -> tuple:
    """
    Parse date range strings.

    Args:
        from_date: Start date string
        to_date: End date string

    Returns:
        Tuple of (from_datetime, to_datetime)
    """
    from_dt = parse_date(from_date) if from_date else None
    to_dt = parse_date(to_date) if to_date else None

    return from_dt, to_dt


def is_date_in_range(
    date: datetime,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> bool:
    """
    Check if date falls within range.

    Args:
        date: Date to check
        from_date: Start of range (inclusive)
        to_date: End of range (inclusive)

    Returns:
        True if date is in range, False otherwise
    """
    if from_date and date < from_date:
        return False
    if to_date and date > to_date:
        return False
    return True


def get_current_datetime() -> datetime:
    """Get current UTC datetime"""
    return datetime.utcnow()


def get_current_iso_string() -> str:
    """Get current datetime as ISO string"""
    return format_date_iso(get_current_datetime())