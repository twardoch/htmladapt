# this_file: tests/test_parser.py
"""Tests for HTMLParser class."""

import pytest
from htmladapt.core.parser import HTMLParser


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

    def test_parser_preference(self):
        """Test parser preference configuration."""
        parser = HTMLParser(parser_preference=["html.parser", "lxml"])

        # Should work with html.parser (always available)
        html = "<html><body><p>Test</p></body></html>"
        soup = parser.parse(html)
        assert soup.find("p").get_text() == "Test"

    def test_available_parsers(self):
        """Test available parsers property."""
        parsers = self.parser.available_parsers

        # html.parser should always be available
        assert "html.parser" in parsers
        assert isinstance(parsers, list)

    def test_parser_info(self):
        """Test parser info functionality."""
        info = self.parser.get_parser_info()

        assert isinstance(info, dict)
        assert "html.parser" in info
        assert info["html.parser"] is True  # Always available

    def test_clone_preserves_parser_choice(self):
        """Cloning should reuse the parser chosen for the original soup."""
        parser = HTMLParser(parser_preference=["html.parser"])
        soup = parser.parse("<html><body><p>Clone</p></body></html>")

        clone = parser.clone_soup(soup)

        assert getattr(soup, "_htmladapt_parser") == getattr(clone, "_htmladapt_parser")
        assert type(soup.builder) is type(clone.builder)

    def test_html_validation_valid(self):
        """Test HTML validation with valid HTML."""
        valid_html = "<!DOCTYPE html><html><body><p>Valid HTML</p></body></html>"
        is_valid, issues = self.parser.validate_html(valid_html)

        assert is_valid is True
        assert len(issues) == 0

    def test_html_validation_warnings(self):
        """Test HTML validation with warnings."""
        html_no_doctype = "<html><body><p>No DOCTYPE</p></body></html>"
        is_valid, issues = self.parser.validate_html(html_no_doctype)

        # Should be valid with warnings
        assert len(issues) > 0
        assert any("DOCTYPE" in issue for issue in issues)

    def test_html_validation_invalid(self):
        """Test HTML validation with invalid HTML."""
        invalid_html = "<html><body><p>Unclosed tags"
        is_valid, issues = self.parser.validate_html(invalid_html)

        assert len(issues) > 0

    def test_decode_content_utf8(self):
        """Test content decoding with UTF-8."""
        content = "Hello, 世界!".encode()
        decoded = self.parser._decode_content(content)

        assert decoded == "Hello, 世界!"

    def test_decode_content_fallback(self):
        """Test content decoding with fallback to replacement."""
        # Create invalid UTF-8 bytes
        invalid_bytes = b"\xff\xfe\x00\x00invalid"
        decoded = self.parser._decode_content(invalid_bytes)

        # Should not raise exception and return somecompg
        assert isinstance(decoded, str)
