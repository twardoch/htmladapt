# this_file: src/htmladapt/utils/helpers.py
"""Utility helper functions for HTMLAdapt."""

import logging
from typing import Tuple, List

from htmladapt.core.parser import HTMLParser

logger = logging.getLogger(__name__)


def validate_html(content: str) -> tuple[bool, list[str]]:
    """Validate HTML content and return any parsing issues.

    Args:
        content: HTML content to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    parser = HTMLParser()
    return parser.validate_html(content)


def estimate_processing_time(content: str) -> tuple[float, int]:
    """Estimate processing time and memory requirements for HTML content.

    Args:
        content: HTML content to analyze

    Returns:
        Tuple of (estimated_time_seconds, estimated_memory_mb)
    """
    # Simple estimation based on content size and complexity
    content_size = len(content)

    # Count HTML elements for complexity estimation
    tag_count = content.count('<')

    # Base processing time: ~1ms per KB
    base_time = content_size / (1024 * 1000)  # seconds

    # Add complexity factor based on tag count
    complexity_factor = min(tag_count / 1000, 5.0)  # Cap at 5x
    estimated_time = base_time * (1 + complexity_factor)

    # Memory estimation: ~4x content size for processing
    estimated_memory = max(int(content_size * 4 / (1024 * 1024)), 1)  # MB

    return estimated_time, estimated_memory


def optimize_for_size(content: str, target_size_mb: int) -> str:
    """Optimize HTML content for memory constraints.

    Args:
        content: HTML content to optimize
        target_size_mb: Target size in megabytes

    Returns:
        Optimized HTML content
    """
    current_size_mb = len(content.encode('utf-8')) / (1024 * 1024)

    if current_size_mb <= target_size_mb:
        return content

    logger.warning(f"Content size ({current_size_mb:.1f}MB) exceeds target ({target_size_mb}MB)")

    # Simple optimization: remove extra whitespace
    lines = content.split('\n')
    optimized_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped:  # Keep non-empty lines
            optimized_lines.append(stripped)

    optimized_content = '\n'.join(optimized_lines)

    new_size_mb = len(optimized_content.encode('utf-8')) / (1024 * 1024)
    logger.info(f"Optimized content from {current_size_mb:.1f}MB to {new_size_mb:.1f}MB")

    return optimized_content