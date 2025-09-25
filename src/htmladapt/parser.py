# this_file: src/htmladapt/parser.py
"""HTML parsing with multiple backend support and fallback mechanisms."""

import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTMLParser:
    """Simple HTML parser with automatic fallback."""

    def __init__(self) -> None:
        """Initialize the parser."""
        self._preferred_parsers = ["lxml", "html5lib", "html.parser"]

    def parse(self, content: str | bytes, encoding: str | None = None) -> BeautifulSoup:
        """Parse HTML content using the first available parser.

        Args:
            content: HTML content to parse
            encoding: Character encoding to use for bytes content

        Returns:
            BeautifulSoup: Parsed HTML tree

        Raises:
            ValueError: If all parsing attempts fail
        """
        if isinstance(content, bytes):
            content = content.decode(encoding) if encoding else content.decode("utf-8", errors="replace")

        for parser_name in self._preferred_parsers:
            try:
                soup = BeautifulSoup(content, parser_name)
                soup._htmladapt_parser = parser_name
                return soup
            except Exception:
                continue

        # Fallback to basic parser
        soup = BeautifulSoup(content, "html.parser")
        soup._htmladapt_parser = "html.parser"
        return soup

    def clone_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Clone a soup object using the same parser that created it."""
        parser_name = getattr(soup, "_htmladapt_parser", "html.parser")
        clone = BeautifulSoup(str(soup), parser_name)
        clone._htmladapt_parser = parser_name
        return clone
