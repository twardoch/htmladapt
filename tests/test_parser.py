# this_file: tests/test_parser.py
"""Tests for HTMLParser class."""

import pytest

from htmladapt.parser import HTMLParser


class TestHTMLParser:
    """Test HTMLParser functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = HTMLParser()

    def test_basic_parsing(self):
        """Test basic HTML parsing."""
        html = "<html><body><p>Hello, World!</p></body></html>"
        soup = self.parser.parse(html)

        assert soup.find("p").get_text() == "Hello, World!"

    def test_malformed_html_parsing(self):
        """Test parsing of malformed HTML."""
        malformed_html = "<html><body><p>Unclosed paragraph</body></html>"
        soup = self.parser.parse(malformed_html)

        # Should still be parseable
        assert soup.find("body") is not None

    def test_empty_html_parsing(self):
        """Test parsing empty HTML."""
        empty_html = ""
        soup = self.parser.parse(empty_html)

        # Should not raise exception
        assert soup is not None

    def test_bytes_input_utf8(self):
        """Test parsing bytes input with UTF-8 encoding."""
        html_bytes = b"<html><body><p>Hello, World!</p></body></html>"
        soup = self.parser.parse(html_bytes)

        assert soup.find("p").get_text() == "Hello, World!"

    def test_bytes_input_with_encoding(self):
        """Test parsing bytes input with specified encoding."""
        html_bytes = b"<html><body><p>Hello, World!</p></body></html>"
        soup = self.parser.parse(html_bytes, encoding="utf-8")

        assert soup.find("p").get_text() == "Hello, World!"

    def test_clone_preserves_parser_choice(self):
        """Cloning should reuse the parser chosen for the original soup."""
        soup = self.parser.parse("<html><body><p>Clone</p></body></html>")
        clone = self.parser.clone_soup(soup)

        assert hasattr(clone, "_htmladapt_parser")
        assert clone.find("p").get_text() == "Clone"
