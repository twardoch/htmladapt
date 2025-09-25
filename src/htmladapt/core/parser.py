# this_file: src/htmladapt/core/parser.py
"""HTML parsing with multiple backend support and fallback mechanisms."""

import logging
from typing import Optional, Union

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTMLParser:
    """Multi-backend HTML parser with fallback support.

    Supports parsing HTML with lxml (fast), html5lib (tolerant), and html.parser
    (built-in) backends with automatic fallback on parsing errors.
    """

    def __init__(self, parser_preference: list[str] | None = None) -> None:
        """Initialize the parser with preferred backend order.

        Args:
            parser_preference: Ordered list of parser backends to try
        """
        self.parser_preference = parser_preference or ["lxml", "html5lib", "html.parser"]
        self._available_parsers = self._check_available_parsers()

    def _check_available_parsers(self) -> list[str]:
        """Check which parsers are available on the system.

        Returns:
            List of available parser names
        """
        available = []

        # Check lxml
        try:
            import lxml
            available.append("lxml")
        except ImportError:
            logger.debug("lxml parser not available")

        # Check html5lib
        try:
            import html5lib
            available.append("html5lib")
        except ImportError:
            logger.debug("html5lib parser not available")

        # html.parser is always available
        available.append("html.parser")

        return available

    def parse(self, content: str | bytes, encoding: str | None = None) -> BeautifulSoup:
        """Parse HTML content using the first available parser.

        Args:
            content: HTML content to parse
            encoding: Character encoding to use for bytes content

        Returns:
            BeautifulSoup: Parsed HTML tree

        Raises:
            ValueError: If no parsers are available or all parsing attempts fail
        """
        if isinstance(content, bytes):
            if encoding:
                content = content.decode(encoding)
            else:
                # Try to detect encoding
                content = self._decode_content(content)

        last_exception = None
        attempted_parsers = []

        for parser_name in self.parser_preference:
            if parser_name not in self._available_parsers:
                continue

            try:
                logger.debug(f"Attempting to parse with {parser_name}")
                soup = BeautifulSoup(content, parser_name)
                logger.debug(f"Successfully parsed with {parser_name}")
                return soup

            except Exception as e:
                logger.debug(f"Parser {parser_name} failed: {e}")
                last_exception = e
                attempted_parsers.append(parser_name)
                continue

        # If we get here, all parsers failed
        error_msg = f"All parsers failed. Attempted: {attempted_parsers}"
        if last_exception:
            error_msg += f". Last error: {last_exception}"

        raise ValueError(error_msg)

    def _decode_content(self, content: bytes) -> str:
        """Attempt to decode bytes content with common encodings.

        Args:
            content: Bytes content to decode

        Returns:
            Decoded string content

        Raises:
            UnicodeDecodeError: If content cannot be decoded
        """
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]

        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        # Last resort - decode with errors='replace'
        return content.decode("utf-8", errors="replace")

    def validate_html(self, content: str) -> tuple[bool, list[str]]:
        """Validate HTML content and return any parsing issues.

        Args:
            content: HTML content to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        try:
            soup = self.parse(content)

            # Check for common issues
            if not soup.find():
                issues.append("No HTML elements found")

            # Check for unclosed tags (simplified check)
            if content.count('<') != content.count('>'):
                issues.append("Mismatched angle brackets")

            # Check for missing doctype (warning, not error)
            if not content.strip().lower().startswith('<!doctype'):
                issues.append("No DOCTYPE declaration (warning)")

            return len(issues) == 0 or all("warning" in issue.lower() for issue in issues), issues

        except Exception as e:
            issues.append(f"Parsing error: {str(e)}")
            return False, issues

    @property
    def available_parsers(self) -> list[str]:
        """Get list of available parser backends.

        Returns:
            List of available parser names
        """
        return self._available_parsers.copy()

    def get_parser_info(self) -> dict[str, bool]:
        """Get information about parser availability.

        Returns:
            Dictionary mapping parser names to availability status
        """
        return {
            "lxml": "lxml" in self._available_parsers,
            "html5lib": "html5lib" in self._available_parsers,
            "html.parser": True,  # Always available
        }