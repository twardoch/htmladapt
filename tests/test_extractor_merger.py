# this_file: tests/test_extractor_merger.py
"""Tests for HTMLExtractMergeTool class."""

import pytest
from htmladapt.core.extractor_merger import HTMLExtractMergeTool
from htmladapt.core.config import ProcessingConfig


class TestHTMLExtractMergeTool:
    """Test HTMLExtractMergeTool functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = HTMLExtractMergeTool()

    def test_basic_extraction(self):
        """Test basic HTML extraction."""
        html = """
        <html>
            <head><title>Test Document</title></head>
            <body>
                <h1>Main Title</h1>
                <p>First paragraph with text.</p>
                <p>Second paragraph with more text.</p>
            </body>
        </html>
        """

        superset, subset = self.tool.extract(html)

        # Check that superset contains IDs
        assert "auto_" in superset  # Generated IDs should be present

        # Check that subset contains translatable content
        assert "Main Title" in subset
        assert "First paragraph" in subset
        assert "Second paragraph" in subset

    def test_extraction_with_existing_ids(self):
        """Test extraction preserving existing IDs."""
        html = """
        <html>
            <body>
                <p id="existing">Paragraph with existing ID.</p>
                <p>Paragraph without ID.</p>
            </body>
        </html>
        """

        superset, subset = self.tool.extract(html)

        # Existing ID should be preserved
        assert 'id="existing"' in superset
        assert 'id="existing"' in subset

        # New ID should be generated for paragraph without ID
        assert "auto_" in superset

    def test_basic_merge(self):
        """Test basic HTML merge operation."""
        original_html = """
        <html>
            <body>
                <p>Original text.</p>
            </body>
        </html>
        """

        # Extract
        superset, subset = self.tool.extract(original_html)

        # Edit (simulate translation)
        edited_subset = subset.replace("Original text", "Edited text")

        # Merge
        result = self.tool.merge(edited_subset, subset, superset, original_html)

        # Check result
        assert "Edited text" in result
        assert "Original text" not in result

    def test_complex_html_extraction(self):
        """Test extraction with complex HTML structure."""
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Complex Document</title>
                <style>body { margin: 0; }</style>
                <script>console.log('test');</script>
            </head>
            <body>
                <header>
                    <nav>
                        <a href="/">Home</a>
                        <a href="/about">About</a>
                    </nav>
                </header>
                <main>
                    <article>
                        <h1>Article Title</h1>
                        <p>Article content goes here.</p>
                        <blockquote>This is a quote.</blockquote>
                    </article>
                </main>
                <footer>
                    <p>&copy; 2024 Test Company</p>
                </footer>
            </body>
        </html>
        """

        superset, subset = self.tool.extract(html)

        # Should preserve structure
        assert "<html>" in superset
        assert "<head>" in superset
        assert "<style>" in superset  # Non-translatable content preserved
        assert "<script>" in superset  # Non-translatable content preserved

        # Subset should contain only translatable text
        assert "Home" in subset
        assert "About" in subset
        assert "Article Title" in subset
        assert "Article content" in subset
        assert "This is a quote" in subset

    def test_empty_html_handling(self):
        """Test handling of empty or minimal HTML."""
        empty_html = ""
        minimal_html = "<html></html>"

        # Should not crash on empty HTML
        try:
            superset1, subset1 = self.tool.extract(empty_html)
            superset2, subset2 = self.tool.extract(minimal_html)

            # Basic validation
            assert isinstance(superset1, str)
            assert isinstance(subset1, str)
            assert isinstance(superset2, str)
            assert isinstance(subset2, str)

        except Exception as e:
            pytest.fail(f"Empty HTML handling failed: {e}")

    def test_validation_functionality(self):
        """Test HTML validation functionality."""
        valid_html = "<html><body><p>Valid content</p></body></html>"
        invalid_html = "<html><body><p>Unclosed tag"

        is_valid, issues = self.tool.validate_html(valid_html)
        assert len(issues) == 0 or all("warning" in issue.lower() for issue in issues)

        is_invalid, invalid_issues = self.tool.validate_html(invalid_html)
        assert len(invalid_issues) > 0

    def test_stats_functionality(self):
        """Test statistics functionality."""
        stats = self.tool.stats

        assert isinstance(stats, dict)
        assert "config_profile" in stats
        assert "available_parsers" in stats
        assert "similarity_threshold" in stats

    def test_custom_config(self):
        """Test tool with custom configuration."""
        config = ProcessingConfig(
            id_prefix="custom_",
            similarity_threshold=0.9,
            performance_profile="accurate"
        )

        tool = HTMLExtractMergeTool(config=config)
        html = "<html><body><p>Test text</p></body></html>"

        superset, subset = tool.extract(html)

        # Should use custom prefix
        assert "custom_" in superset

    def test_text_containing_element_detection(self):
        """Test detection of text-containing elements."""
        html = """
        <html>
            <body>
                <p>Text paragraph</p>
                <div></div>
                <span>Text span</span>
                <script>console.log('not text');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """

        superset, subset = self.tool.extract(html)

        # Text-containing elements should be in subset
        assert "Text paragraph" in subset
        assert "Text span" in subset

        # Non-text elements should not be in subset
        assert "console.log" not in subset
        assert "color: red" not in subset

    def test_merge_with_no_changes(self):
        """Test merge when no changes were made."""
        html = "<html><body><p>Unchanged text</p></body></html>"

        superset, subset = self.tool.extract(html)
        result = self.tool.merge(subset, subset, superset, html)

        # Should be essentially the same as original
        assert "Unchanged text" in result

    def test_element_text_extraction(self):
        """Test internal text extraction functionality."""
        from bs4 import BeautifulSoup

        html = '<p>Simple <strong>bold</strong> text with <em>emphasis</em>.</p>'
        soup = BeautifulSoup(html, 'html.parser')
        p_tag = soup.find('p')

        text = self.tool._extract_text_content(p_tag)
        # Normalize whitespace for comparison
        normalized_text = ' '.join(text.split())
        assert "Simple bold text with emphasis." in normalized_text