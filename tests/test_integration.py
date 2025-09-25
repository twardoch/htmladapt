# this_file: tests/test_integration.py
"""Integration tests for HTMLAdapt end-to-end workflows."""

import pytest
from htmladapt import HTMLExtractMergeTool, ProcessingConfig


class TestIntegration:
    """Integration tests for complete extract-merge workflows."""

    def test_simple_translation_workflow(self):
        """Test a simple translation workflow."""
        original_html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <title>Welcome Page</title>
                <meta charset="utf-8">
            </head>
            <body>
                <header>
                    <h1>Welcome to Our Website</h1>
                    <nav>
                        <a href="/">Home</a>
                        <a href="/about">About Us</a>
                        <a href="/contact">Contact</a>
                    </nav>
                </header>
                <main>
                    <section>
                        <h2>Our Services</h2>
                        <p>We provide excellent services to our customers.</p>
                        <ul>
                            <li>Web Development</li>
                            <li>Mobile Apps</li>
                            <li>Consulting</li>
                        </ul>
                    </section>
                </main>
                <footer>
                    <p>&copy; 2024 Our Company. All rights reserved.</p>
                </footer>
            </body>
        </html>
        """

        tool = HTMLExtractMergeTool()

        # Step 1: Extract content
        superset, subset = tool.extract(original_html)

        # Verify extraction
        assert "Welcome to Our Website" in subset
        assert "Our Services" in subset
        assert "Web Development" in subset

        # Step 2: Simulate translation (English to Spanish)
        translations = {
            "Welcome to Our Website": "Bienvenido a Nuestro Sitio Web",
            "Home": "Inicio",
            "About Us": "Acerca de Nosotros",
            "Contact": "Contacto",
            "Our Services": "Nuestros Servicios",
            "We provide excellent services to our customers.": "Proporcionamos excelentes servicios a nuestros clientes.",
            "Web Development": "Desarrollo Web",
            "Mobile Apps": "Aplicaciones Móviles",
            "Consulting": "Consultoría",
            "All rights reserved.": "Todos los derechos reservados."
        }

        edited_subset = subset
        for english, spanish in translations.items():
            edited_subset = edited_subset.replace(english, spanish)

        # Step 3: Merge back
        result = tool.merge(edited_subset, subset, superset, original_html)

        # Verify merge results
        assert "Bienvenido a Nuestro Sitio Web" in result
        assert "Nuestros Servicios" in result
        assert "Desarrollo Web" in result
        assert "Todos los derechos reservados" in result

        # Verify structure preservation
        assert "<!DOCTYPE html>" in result
        assert '<html lang="en">' in result
        assert 'charset="utf-8"' in result  # Accept both <meta charset="utf-8"> and <meta charset="utf-8"/>
        assert "<header>" in result
        assert "<nav>" in result
        assert "<main>" in result
        assert "<footer>" in result

    def test_content_editing_workflow(self):
        """Test a content editing workflow."""
        original_html = """
        <html>
            <body>
                <article>
                    <h1>Old Article Title</h1>
                    <p>This is the old introduction paragraph.</p>
                    <p>Here is some old content that needs updating.</p>
                    <p>This paragraph will remain unchanged.</p>
                </article>
            </body>
        </html>
        """

        tool = HTMLExtractMergeTool()

        # Extract
        superset, subset = tool.extract(original_html)

        # Edit content
        edited_subset = subset.replace("Old Article Title", "New Article Title")
        edited_subset = edited_subset.replace(
            "This is the old introduction paragraph.",
            "This is the updated introduction with new information."
        )
        edited_subset = edited_subset.replace(
            "Here is some old content that needs updating.",
            "Here is the fresh, updated content."
        )

        # Merge
        result = tool.merge(edited_subset, subset, superset, original_html)

        # Verify changes
        assert "New Article Title" in result
        assert "updated introduction with new information" in result
        assert "fresh, updated content" in result
        assert "This paragraph will remain unchanged." in result

        # Verify structure preservation
        assert "<article>" in result
        assert result.count("<p>") == 3  # Should still have 3 paragraphs

    def test_partial_translation_workflow(self):
        """Test workflow where only some content is translated."""
        original_html = """
        <html>
            <body>
                <h1>Mixed Content</h1>
                <p>This will be translated.</p>
                <p>This will not be translated.</p>
                <p>Este ya está en español.</p>
            </body>
        </html>
        """

        tool = HTMLExtractMergeTool()

        superset, subset = tool.extract(original_html)

        # Only translate the first paragraph
        edited_subset = subset.replace(
            "This will be translated.",
            "Esto será traducido."
        )

        result = tool.merge(edited_subset, subset, superset, original_html)

        # Verify partial translation
        assert "Esto será traducido." in result
        assert "This will not be translated." in result  # Unchanged
        assert "Este ya está en español." in result  # Unchanged

    def test_workflow_with_custom_config(self):
        """Test workflow with custom configuration."""
        config = ProcessingConfig(
            id_prefix="trans_",
            similarity_threshold=0.8,
            performance_profile="accurate"
        )

        tool = HTMLExtractMergeTool(config=config)

        html = """
        <html>
            <body>
                <h1>Test Title</h1>
                <p>Test paragraph content.</p>
            </body>
        </html>
        """

        superset, subset = tool.extract(html)
        edited_subset = subset.replace("Test Title", "Updated Title")
        result = tool.merge(edited_subset, subset, superset, html)

        assert "Updated Title" in result
        # Should use custom prefix (visible in superset)
        assert "trans_" in superset

    def test_malformed_html_workflow(self):
        """Test workflow with malformed HTML."""
        malformed_html = """
        <html>
            <body>
                <h1>Title with unclosed tag
                <p>Paragraph without closing
                <div>Content in div</div>
            </body>
        </html>
        """

        tool = HTMLExtractMergeTool()

        # Should handle malformed HTML gracefully
        superset, subset = tool.extract(malformed_html)
        edited_subset = subset.replace("Title", "New Title")
        result = tool.merge(edited_subset, subset, superset, malformed_html)

        assert "New Title" in result

    def test_large_document_workflow(self):
        """Test workflow with a larger document."""
        # Generate a larger HTML document
        sections = []
        for i in range(20):
            sections.append(f"""
            <section>
                <h2>Section {i+1}</h2>
                <p>This is paragraph 1 in section {i+1}.</p>
                <p>This is paragraph 2 in section {i+1}.</p>
                <p>This is paragraph 3 in section {i+1}.</p>
            </section>
            """)

        large_html = f"""
        <html>
            <body>
                <h1>Large Document</h1>
                {''.join(sections)}
            </body>
        </html>
        """

        tool = HTMLExtractMergeTool()

        # Should handle large documents
        superset, subset = tool.extract(large_html)

        # Edit some content
        edited_subset = subset.replace("Large Document", "Documento Grande")

        result = tool.merge(edited_subset, subset, superset, large_html)

        assert "Documento Grande" in result
        assert result.count("<section>") == 20  # All sections preserved

    def test_round_trip_preservation(self):
        """Test that content is preserved in round-trip processing."""
        original_html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <title>Preservation Test</title>
                <meta charset="utf-8">
                <style>
                    body { margin: 0; padding: 20px; }
                    .highlight { background-color: yellow; }
                </style>
                <script>
                    function test() {
                        console.log('test function');
                    }
                </script>
            </head>
            <body class="main-body" data-version="1.0">
                <header id="main-header">
                    <h1 class="title">Test Document</h1>
                </header>
                <main>
                    <p class="intro">Introduction paragraph.</p>
                    <div class="content">
                        <p>Content paragraph 1.</p>
                        <p>Content paragraph 2.</p>
                    </div>
                </main>
                <footer>
                    <p>&copy; 2024</p>
                </footer>
            </body>
        </html>
        """

        tool = HTMLExtractMergeTool()

        # Extract and merge without changes
        superset, subset = tool.extract(original_html)
        result = tool.merge(subset, subset, superset, original_html)

        # Key structural elements should be preserved
        assert "<!DOCTYPE html>" in result
        assert 'lang="en"' in result
        assert "<style>" in result and "</style>" in result
        assert "<script>" in result and "</script>" in result
        assert 'class="main-body"' in result
        assert 'data-version="1.0"' in result
        assert 'id="main-header"' in result
        assert 'class="title"' in result
        assert 'class="intro"' in result
        assert 'class="content"' in result

        # Content should be preserved
        assert "Test Document" in result
        assert "Introduction paragraph." in result
        assert "Content paragraph 1." in result
        assert "Content paragraph 2." in result